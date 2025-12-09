import datetime
from io import BytesIO

from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.core.management import call_command
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import FormView
from xlsxwriter import Workbook

from juntagrico import __version__
from juntagrico.config import Config
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionpartdao import SubscriptionPartDao
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subtypes import SubscriptionBundle
from juntagrico.forms import GenerateListForm, ShiftTimeForm
from juntagrico.util import return_to_previous_location, addons
from juntagrico.util.management_list import get_changedate
from juntagrico.util.pdf import return_pdf_http
from juntagrico.util.views_admin import subscription_management_list
from juntagrico.util.xls import generate_excel
from juntagrico.views_subscription import error_page


@permission_required('juntagrico.can_view_lists')
def depotlist(request):
    return return_pdf_http('depotlist.pdf')


@permission_required('juntagrico.can_view_lists')
def depot_overview(request):
    return return_pdf_http('depot_overview.pdf')


@permission_required('juntagrico.can_view_lists')
def amount_overview(request):
    return return_pdf_http('amount_overview.pdf')


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
    for subscription in SubscriptionDao.all_active_subscritions():
        for subscription_bundle in subscriptionbundles:
            subscription_lines[subscription_bundle]['now'] += subscription.subscription_amount(
                subscription_bundle)

    for subscription in SubscriptionDao.future_subscriptions():
        for subscription_bundle in subscriptionbundles:
            subscription_lines[subscription_bundle]['future'] += subscription.subscription_amount_future(
                subscription_bundle)

    renderdict = {
        'changed': request.GET.get('changed'),
        'subscription_lines': iter(subscription_lines.values()),
    }
    return render(request, 'future.html', renderdict)


@permission_required('juntagrico.can_view_exports')
def excel_export_members_filter(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = Workbook(output)
    worksheet_s = workbook.add_worksheet(str(Config.vocabulary('member_pl')))

    worksheet_s.write_string(0, 0, str(_('Name')))
    worksheet_s.write_string(0, 1, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(
        0, 2, str(Config.vocabulary('assignment') + ' ' + str(_('Kernbereich'))))
    worksheet_s.write_string(0, 3, str(_('Taetigkeitsbereiche')))
    worksheet_s.write_string(0, 4, str(_('Depot')))
    worksheet_s.write_string(0, 5, str(_('Email')))
    worksheet_s.write_string(0, 6, str(_('Telefon')))
    worksheet_s.write_string(0, 7, str(_('Mobile')))

    row = 1
    for member in Member.objects.annotate_all_assignment_count():
        member.all_areas = ''
        for area in member.areas.all():
            member.all_areas = member.all_areas + area.name + ' '
        if member.all_areas == '':
            member.all_areas = str(_('-Kein Tätigkeitsbereich-'))

        member.depot_name = str(_('Kein Depot definiert'))
        if member.subscription_current is not None:
            member.depot_name = member.subscription_current.depot.name
        full_name = member.first_name + ' ' + member.last_name
        worksheet_s.write_string(row, 0, full_name)
        worksheet_s.write(row, 1, member.assignment_count)
        worksheet_s.write(row, 2, member.core_assignment_count)
        worksheet_s.write_string(row, 3, member.all_areas)
        worksheet_s.write_string(row, 4, member.depot_name)
        worksheet_s.write_string(row, 5, member.email)
        worksheet_s.write_string(row, 6, member.phone)
        if member.mobile_phone is not None:
            worksheet_s.write_string(row, 7, member.mobile_phone)
        row += 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response


@permission_required('juntagrico.can_view_exports')
def excel_export_subscriptions(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = Workbook(output)
    worksheet_s = workbook.add_worksheet(str(Config.vocabulary('subscription_pl')))

    worksheet_s.write_string(0, 0, str(_('Übersicht')))
    worksheet_s.write_string(0, 1, str(_('HauptbezieherIn')))
    worksheet_s.write_string(0, 2, str(_('HauptbezieherInEmail')))
    worksheet_s.write_string(0, 3, str(_('HauptbezieherInTelefon')))
    worksheet_s.write_string(0, 4, str(_('HauptbezieherInMobile')))
    worksheet_s.write_string(0, 5, str(_('Weitere BezieherInnen')))
    worksheet_s.write_string(0, 6, str(_('Status')))
    worksheet_s.write_string(0, 7, str(_('Kündigungsdatum')))
    worksheet_s.write_string(0, 8, str(_('Depot')))
    worksheet_s.write_string(0, 9, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(0, 10, str(_('{} soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 11, str(_('{} status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 12, str(_('{} Kernbereich'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 13, str(_('{} Kernbereich soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 14, str(_('{} Kernbereich status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 15, str(_('Preis')))

    subs = SubscriptionDao.all_subscritions().annotate_assignments_progress().select_related('primary_member')

    row = 1
    for sub in subs:
        primary_member = sub.primary_member
        if primary_member is not None:
            name = primary_member.get_name()
            email = primary_member.email
            phone = primary_member.phone or ''
            mobile = primary_member.mobile_phone or ''
        else:
            name = ''
            email = ''
            phone = ''
            mobile = ''

        c_date = ''
        if sub.cancellation_date:
            c_date = sub.cancellation_date.strftime('%d/%m/%y')

        worksheet_s.write_string(row, 0, sub.size)
        worksheet_s.write_string(row, 1, name)
        worksheet_s.write_string(row, 2, email)
        worksheet_s.write_string(row, 3, phone)
        worksheet_s.write_string(row, 4, mobile)
        worksheet_s.write_string(row, 5, ', '.join(str(m) for m in sub.co_members()))
        worksheet_s.write_string(row, 6, sub.state_text)
        worksheet_s.write_string(row, 7, c_date)
        worksheet_s.write_string(row, 8, sub.depot.name)
        worksheet_s.write(row, 9, sub.assignment_count)
        worksheet_s.write(row, 10, sub.required_assignments)
        worksheet_s.write(row, 11, sub.assignments_progress)
        worksheet_s.write(row, 12, sub.core_assignment_count)
        worksheet_s.write(row, 13, sub.required_core_assignments)
        worksheet_s.write(row, 14, sub.core_assignments_progress)
        worksheet_s.write(row, 15, sub.price)
        row += 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response


@permission_required('juntagrico.can_view_exports')
def excel_export_members(request):
    fields = [
        'first_name',
        'last_name',
        'email',
        'addr_street',
        'addr_zipcode',
        'addr_location',
        'birthday',
        'phone',
        'mobile_phone',
        'confirmed',
        'reachable_by_email',
        'deactivation_date',
    ]
    return generate_excel(fields, Member)


@permission_required('juntagrico.can_view_exports')
def excel_export_shares(request):
    fields = [
        'id',
        'number',
        'paid_date',
        'issue_date',
        'booking_date',
        'cancelled_date',
        'termination_date',
        'payback_date',
        'notes',
        'member.first_name',
        'member.last_name',
        'member.email',
    ]
    return generate_excel(fields, Share)


@permission_required('juntagrico.can_view_exports')
def export(request):
    return render(request, 'export.html', {})


@permission_required('juntagrico.change_subscription')
def waitinglist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionDao.not_started_subscriptions(), render_dict,
                                        'management_lists/waitinglist.html', request)


@permission_required('juntagrico.change_subscription')
def canceledlist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionDao.canceled_subscriptions(), render_dict,
                                        'management_lists/canceledlist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def part_waitinglist(request):
    render_dict = get_changedate(request)
    changedlist = SubscriptionPartDao.waiting_parts_for_active_subscriptions()
    return subscription_management_list(changedlist, render_dict, 'management_lists/part_waitinglist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def part_canceledlist(request):
    render_dict = get_changedate(request)
    changedlist = SubscriptionPartDao.canceled_parts_for_active_subscriptions()
    return subscription_management_list(changedlist, render_dict, 'management_lists/part_canceledlist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def extra_waitinglist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionPartDao.waiting_extra_subs(), render_dict,
                                        'management_lists/extra_waitinglist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def extra_canceledlist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionPartDao.canceled_extra_subs(), render_dict,
                                        'management_lists/extra_canceledlist.html', request)


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


@permission_required('juntagrico.can_generate_lists')
def manage_list(request):
    success = False
    can_change_subscription = request.user.has_perm('juntagrico.change_subscription')
    if request.method == 'POST':
        form = GenerateListForm(request.POST, show_future=can_change_subscription)
        if form.is_valid():
            # generate list
            f = can_change_subscription and form.cleaned_data['future']
            call_command('generate_depot_list', force=True, future=f, no_future=not f, days=(form.cleaned_data['for_date'] - datetime.date.today()).days)
            success = True
    else:
        form = GenerateListForm(show_future=can_change_subscription)
    return render(request, 'juntagrico/manage/list.html', {'form': form, 'success': success})


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
