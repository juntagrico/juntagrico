from django.db import transaction
from django.db.models import F
from django.forms import model_to_dict
from django.shortcuts import redirect, render
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.utils.module_loading import import_string
from django.http import Http404, JsonResponse
from django import forms
from django.core.exceptions import BadRequest
from django.urls import reverse

from juntagrico.config import Config
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.forms import SubscriptionPartSelectForm, StartDateForm, EditCoMemberForm, RegisterMultiCoMemberForm, \
    RegisterFirstMultiCoMemberForm, ShareOrderForm, RegisterSummaryForm, SubscriptionExtraPartSelectForm, \
    SubscriptionPartSelectRequiredForm
from juntagrico.util import temporal
from juntagrico.view_decorators import signup_session
from juntagrico.views_subscription import SignupView


@signup_session
def select_parts(
        request, signup_manager,
        key='subscriptions',
        form_class=SubscriptionPartSelectForm,
        required_subscription_form_class=SubscriptionPartSelectRequiredForm,
        template_name='juntagrico/subscription/create/select_subscription.html'
):
    if Config.require_subscription():
        form_class = required_subscription_form_class
    subscriptions = signup_manager.get(key, {})
    if request.method == 'POST':
        form = form_class(subscriptions, request.POST)
        if form.is_valid():
            signup_manager.set(key, {str(t.id): amount for t, amount in form.get_selected().items()})
            return redirect(signup_manager.get_next_page())
    else:
        form = form_class(subscriptions)

    render_dict = {
        'form': form,
        'hours_used': Config.assignment_unit() == 'HOURS',
    }
    return render(request, template_name, render_dict)


def select_extras(request):
    return select_parts(
        request,
        key='extras',
        form_class=SubscriptionExtraPartSelectForm,
        required_subscription_form_class=SubscriptionExtraPartSelectForm,
        template_name='juntagrico/subscription/create/select_extras.html'
    )


@signup_session
def select_depot(request, signup_manager):
    if request.method == 'POST':
        signup_manager.set('depot', request.POST.get('depot'))
        return redirect(signup_manager.get_next_page())

    depots = DepotDao.all_visible_depots_with_map_info()
    selected = signup_manager.get('depot')
    if selected is not None:
        selected = int(selected)

    return render(request, 'juntagrico/subscription/create/select_depot.html', {
        'depots': depots,
        'subscription_count': signup_manager.get('subscriptions', {}),
        'selected': selected,
    })


@signup_session
def select_start_date(request, signup_manager):
    subscription_form = StartDateForm(initial={
        'start_date': signup_manager.get('start_date', temporal.start_of_next_business_year())
    })
    if request.method == 'POST':
        subscription_form = StartDateForm(request.POST)
        if subscription_form.is_valid():
            signup_manager.set('start_date', subscription_form.data['start_date'])
            return redirect(signup_manager.get_next_page())
    render_dict = {
        'start_date': temporal.start_of_next_business_year(),
        'subscriptionform': subscription_form,
    }
    return render(request, 'juntagrico/subscription/create/select_start_date.html', render_dict)


class ExternalSignupForm(forms.Form):
    '''
    Defines the fields and validations for the external signup API, decouple from internal names
    '''
    first_name = forms.CharField()
    family_name = forms.CharField()
    street = forms.CharField()
    house_number = forms.CharField()
    postal_code = forms.CharField()
    city = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()
    depot_id = forms.ModelChoiceField(queryset=DepotDao.all_visible_depots())
    start_date = forms.DateField()
    shares = forms.IntegerField(min_value=0)
    comment = forms.CharField(required=False)
    by_laws_accepted = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        sub_ids = kwargs.pop('sub_ids')
        super(ExternalSignupForm, self).__init__(*args, **kwargs)

        for id in sub_ids:
            self.fields['subscription_%s' % id] = forms.IntegerField(min_value=0, required=False)


@csrf_exempt
def create_external(request):
    '''
    Handle external subscription POST requests and return depot and subscription details on GET

    Usage: curl -k -L -b -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'first_name=John&family_name=Doe&street=Bahnhofstrasse&house_number=42&postal_code=8001&city=Z%C3%BCrich&phone=078%2012345678&email=john.doe@invalid.com&comment=Ich%20freue%20mich%20auf%20den%20Start!&by_laws_accepted=TRUE&subscription_1=1&subscription_2=2&depot_id=1&start_date=2025-12-01&shares=4' 'http://example.com/signup/external'
    '''
    if not Config.enable_external_signup():
        raise Http404
    if request.method == "GET":
        depots = list(DepotDao.all_visible_depots().values('id', 'name'))
        subs = list(SubscriptionType.objects.visible()
                    .annotate(is_extra=F("size__product__is_extra"))
                    .values('id', 'name', 'shares', 'required_assignments', 'required_core_assignments',
                            'price', 'trial', 'description', 'is_extra'))
        external_details = {'depots': depots,
                    'subscriptions': subs}
        return JsonResponse(external_details, safe=False)
    if not request.method == 'POST':
        raise BadRequest("POST request method expected")
    if request.user.is_authenticated:
        logout(request)
    allsubs = SubscriptionType.objects.visible()
    form = ExternalSignupForm(request.POST, sub_ids=list(allsubs.values_list('id', flat=True)))
    if not form.is_valid():
        raise BadRequest("Invalid data submitted")
    post_data = form.cleaned_data
    signup_manager = import_string(Config.signup_manager())(request)
    main_member = {'last_name': post_data['family_name'],
                   'first_name': post_data['first_name'],
                   'addr_street': post_data['street'] + ' ' + post_data['house_number'],
                   'addr_zipcode': post_data['postal_code'],
                   'addr_location': post_data['city'],
                   'phone': post_data['phone'],
                   'email': post_data['email'],
                   'agb': post_data['by_laws_accepted'],
                   'mobile_phone': '',
                   'birthday': '',
                   'submit': 'Anmelden',
                   'comment': post_data['comment'] + '[External signup API]'
                   }
    signup_manager.set('main_member', main_member)
    subs = {str(x.pk): int(post_data['subscription_%s' % x.pk] or 0 if not x.size.product.is_extra else 0) for x in allsubs}
    extras = {str(x.pk): int(post_data['subscription_%s' % x.pk] or 0 if x.size.product.is_extra else 0) for x in allsubs}
    signup_manager.set('subscriptions', subs)
    signup_manager.set('extras', extras)
    depot_id = post_data['depot_id'].pk
    signup_manager.set('depot', depot_id)
    start_date = post_data['start_date'].strftime('%Y-%m-%d')
    signup_manager.set('start_date', start_date)
    signup_manager.set('co_members_done', True)
    shares_amount = post_data['shares']
    signup_manager.set('shares', {'of_member': shares_amount})
    if MemberDao.member_by_email(main_member['email']) or not post_data['by_laws_accepted']:
        # submitted mail address exists in system or by laws acceptance missing, send back to member details form for correction
        return redirect(reverse('signup') + '?mod')
    if all(value == 0 for value in subs.values()):
        # no subscription selected, send back to subscription selection form
        return redirect(reverse('cs-subscription') + '?mod')
    return redirect(signup_manager.get_next_page())


class AddMemberView(SignupView, FormView):
    template_name = 'juntagrico/subscription/create/add_member.html'

    def __init__(self):
        super().__init__()
        self.edit = False
        self.member_data = {}

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.edit = int(request.GET.get('edit', request.POST.get('edit', 0)))
        if request.user.is_authenticated:
            self.member_data = model_to_dict(request.user.member, ['email', 'addr_street', 'addr_zipcode', 'addr_location'])
        else:
            self.member_data = self.signup_manager.get('main_member')

    def get_form_class(self):
        return EditCoMemberForm if self.edit else \
            RegisterMultiCoMemberForm if self.signup_manager.get('co_members') else RegisterFirstMultiCoMemberForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        # edit co-member from list
        own_email = None
        if self.edit:
            if 'data' not in form_kwargs:
                form_kwargs['data'] = self.signup_manager.get('co_members', [])[self.edit - 1]
                form_kwargs['data']['edit'] = self.edit
            own_email = form_kwargs['data']['email'].lower()
        # collect used email addresses to block reusage
        existing_emails = [self.member_data['email'].strip().lower()]
        for co_member in self.signup_manager.get('co_members', []):
            email = co_member['email'].lower()
            if email != own_email:
                existing_emails.append(email)
        form_kwargs['existing_emails'] = existing_emails
        return form_kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            co_members=self.signup_manager.get('co_members', []) if not self.edit else [],
            **kwargs
        )

    def get_initial(self):
        # use address from main member as default
        return {
            'addr_street': self.member_data['addr_street'],
            'addr_zipcode': self.member_data['addr_zipcode'],
            'addr_location': self.member_data['addr_location'],
            'edit': str(self.edit)
        }

    def form_invalid(self, form):
        if form.existing_member:  # use existing member if found
            return self.form_valid(form)
        return super().form_invalid(form)

    def form_valid(self, form):
        # create new member from form data
        return self._add_or_replace_co_member(form.existing_member.email if form.existing_member else form.data.dict())

    def _add_or_replace_co_member(self, member):
        if self.edit:
            self.signup_manager.replace('co_members', self.edit - 1, member)
            return redirect(self.signup_manager.get_next_page())
        else:
            self.signup_manager.append('co_members', member)
            return redirect('.')

    def get(self, request, *args, **kwargs):
        # done: move to next page
        if request.GET.get('next') is not None:
            self.signup_manager.set('co_members_done', True)
            return redirect(self.signup_manager.get_next_page())

        # function: remove co-members from list
        remove_member = int(request.GET.get('remove', 0))
        if remove_member:
            self.signup_manager.remove('co_members', remove_member - 1)
            return redirect(self.signup_manager.get_next_page())

        # render page
        return super().get(request, *args, **kwargs)


class SelectSharesView(SignupView, FormView):
    template_name = 'juntagrico/subscription/create/select_shares.html'
    form_class = ShareOrderForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['required'] = self.signup_manager.required_shares()
        form_kwargs['existing'] = self.signup_manager.existing_shares()
        form_kwargs['co_members'] = self.signup_manager.co_members()
        if 'data' not in form_kwargs:
            form_kwargs['data'] = self.signup_manager.get('shares')
        return form_kwargs

    def form_valid(self, form):
        self.signup_manager.set('shares', form.data.dict())
        return redirect(self.signup_manager.get_next_page())


class SummaryView(SignupView, FormView):
    template_name = 'juntagrico/subscription/create/summary.html'
    form_class = RegisterSummaryForm

    def get_initial(self):
        return {'comment': self.signup_manager.comment()}

    def get_context_data(self, **kwargs):
        args = super().get_context_data(**kwargs)
        args.update(self.signup_manager.data.copy())
        if Config.enable_shares():
            for i, co_member in enumerate(args.get('co_members', [])):
                co_member['new_shares'] = int(args['shares'].get(f'of_co_member[{i}]', 0) or 0)
        args['subscriptions'] = self.signup_manager.subscriptions()
        args['show_extras'] = self.signup_manager.extras_enabled()
        args['extras'] = self.signup_manager.extras()
        args['depot'] = self.signup_manager.depot()
        args['activity_areas'] = ActivityAreaDao.all_auto_add_members_areas()
        return args

    @transaction.atomic
    def form_valid(self, form):
        self.signup_manager.set('comment', form.cleaned_data.get('comment'))
        member = self.signup_manager.apply()
        # finish registration
        if member.subscription_future is None:
            return redirect('welcome')
        return redirect('welcome-with-sub')


def welcome(request, with_sub=False):
    render_dict = {
        'no_subscription': not with_sub
    }
    return render(request, 'welcome.html', render_dict)


@signup_session
def cancel(request, signup_manager):
    signup_manager.clear()
    if request.user.is_authenticated:
        return redirect('subscription-landing')
    else:
        return redirect(Config.organisation_website('url'))
