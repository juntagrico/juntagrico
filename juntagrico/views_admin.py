import datetime

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import FormView

from juntagrico import __version__
from juntagrico.config import Config
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionBundle
from juntagrico.forms import GenerateListForm, ShiftTimeForm
from juntagrico.util import return_to_previous_location, addons
from juntagrico.util.pdf import return_pdf_http
from juntagrico.view_decorators import any_permission_required
from juntagrico.views_subscription import error_page


@permission_required('juntagrico.change_subscription')
def future(request):
    subscriptionbundles = []
    subscription_lines = dict({})
    for subscription_bundle in SubscriptionBundle.objects.order_by('category', 'long_name'):
        subscriptionbundles.append(subscription_bundle.id)
        subscription_lines[subscription_bundle.id] = {
            'name': str(subscription_bundle),
            'future': 0,
            'now': 0
        }
    for subscription in Subscription.objects.active():
        for subscription_bundle in subscriptionbundles:
            subscription_lines[subscription_bundle]['now'] += subscription.subscription_amount(
                subscription_bundle)

    for subscription in Subscription.objects.filter(cancellation_date=None, deactivation_date=None):
        for subscription_bundle in subscriptionbundles:
            subscription_lines[subscription_bundle]['future'] += subscription.subscription_amount_future(
                subscription_bundle)

    renderdict = {
        'changed': request.GET.get('changed'),
        'subscription_lines': iter(subscription_lines.values()),
    }
    return render(request, 'future.html', renderdict)


def set_change_date(request):
    if request.method != 'POST':
        raise Http404
    raw_date = request.POST.get('date')
    try:
        date = datetime.date.fromisoformat(raw_date)
        if date == datetime.date.today():
            raw_date = None
        request.session['changedate'] = raw_date
    except ValueError:
        return error_page(request, _('Bitte gib ein Datum im Format JJJJ-MM-TT ein.'))
    return return_to_previous_location(request)


def unset_change_date(request):
    request.session['changedate'] = None
    return return_to_previous_location(request)


@any_permission_required('juntagrico.can_generate_lists', 'juntagrico.can_view_lists')
def manage_list(request, extra_lists=None):
    extra_lists = extra_lists or []
    depot_lists = []
    if request.user.has_perm('juntagrico.can_view_lists'):
        default_names = dict(
            depotlist=_('{depot}-Listen').format(depot=Config.vocabulary('depot')),
            depot_overview=_('{depot} Übersicht').format(depot=Config.vocabulary('depot')),
            amount_overview=_('Mengen Übersicht')
        )
        for depot_list in list(Config.depot_lists(default_names)) + extra_lists:
            file_name = depot_list['file_name'] + '.pdf'
            exists = default_storage.exists(file_name)
            creation_time = None
            if exists:
                try:
                    creation_time = default_storage.get_created_time(file_name)
                except NotImplementedError:
                    pass
            depot_lists.append({
                **depot_list,
                'exists': exists,
                'creation_time': creation_time,
            })

    form = None
    if request.user.has_perm('juntagrico.can_generate_lists'):
        can_change_subscription = request.user.has_perm('juntagrico.change_subscription')
        if request.method == 'POST':
            form = GenerateListForm(request.POST, show_future=can_change_subscription)
            if form.is_valid():
                # generate list
                f = can_change_subscription and form.cleaned_data['future']
                call_command('generate_depot_list', force=True, future=f, no_future=not f,
                             days=(form.cleaned_data['for_date'] - datetime.date.today()).days)
                messages.success(request, 'Listen erfolgreich erstellt.')
                return HttpResponseRedirect('')
        else:
            form = GenerateListForm(show_future=can_change_subscription)

    return render(request, 'juntagrico/manage/list.html', {
        'depot_lists': depot_lists,
        'form': form,
    })


@permission_required('juntagrico.can_view_lists')
def download_list(request, name, extra_lists=None):
    extra_lists = extra_lists or []
    if name not in [depot_list['file_name'] for depot_list in Config.depot_lists()] + extra_lists:
        raise Http404
    return return_pdf_http(name + '.pdf')


@login_required
def versions(request):
    versions = {'juntagrico': __version__}
    versions.update(addons.config.get_versions())
    render_dict = {'versions': versions}
    return render(request, 'versions.html', render_dict)


@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class ShiftTimeFormView(FormView):
    """
    Show form to call the management command `shift_time`
    """
    success = False
    template_name = "commands/shift_time.html"
    form_class = ShiftTimeForm
    success_url = reverse_lazy('command-shifttime-success')

    def form_valid(self, form):
        call_command('shift_time', form.cleaned_data['hours'],
                     start=form.cleaned_data['start'] or None, end=form.cleaned_data['end'] or None)
        return super().form_valid(form)
