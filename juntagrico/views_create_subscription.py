from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.views.generic import FormView

from juntagrico.config import Config
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.forms import StartDateForm, EditCoMemberForm, RegisterMultiCoMemberForm, \
    RegisterFirstMultiCoMemberForm, SubscriptionPartSelectForm, RegisterSummaryForm, ShareOrderForm
from juntagrico.util import temporal
from juntagrico.view_decorators import signup_session
from juntagrico.views_subscription import SignupView


@signup_session
def cs_select_subscription(request, signup_manager):
    subscriptions = signup_manager.get('subscriptions', {})
    if request.method == 'POST':
        form = SubscriptionPartSelectForm(subscriptions, request.POST)
        if form.is_valid():
            signup_manager.set('subscriptions', {str(t.id): amount for t, amount in form.get_selected().items()})
            return redirect(signup_manager.get_next_page())
    else:
        form = SubscriptionPartSelectForm(subscriptions)

    render_dict = {
        'form': form,
        'hours_used': Config.assignment_unit() == 'HOURS',
    }
    return render(request, 'createsubscription/select_subscription.html', render_dict)


@signup_session
def cs_select_depot(request, signup_manager):
    if request.method == 'POST':
        signup_manager.set('depot', request.POST.get('depot'))
        return redirect(signup_manager.get_next_page())

    depots = DepotDao.all_visible_depots_with_map_info()
    selected = signup_manager.get('depot')
    if selected is not None:
        selected = int(selected)

    return render(request, 'createsubscription/select_depot.html', {
        'depots': depots,
        'subscription_count': signup_manager.get('subscriptions', {}),
        'selected': selected,
    })


@signup_session
def cs_select_start_date(request, signup_manager):
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
    return render(request, 'createsubscription/select_start_date.html', render_dict)


class CSAddMemberView(SignupView, FormView):
    template_name = 'createsubscription/add_member_cs.html'

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


class CSSelectSharesView(SignupView, FormView):
    template_name = 'createsubscription/select_shares.html'
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


class CSSummaryView(SignupView, FormView):
    template_name = 'createsubscription/summary.html'
    form_class = RegisterSummaryForm

    def get_initial(self):
        return {'comment': self.signup_manager.comment()}

    def get_context_data(self, **kwargs):
        args = super().get_context_data(**kwargs)
        args.update(self.signup_manager.data.copy())
        for i, co_member in enumerate(args.get('co_members', [])):
            co_member['new_shares'] = int(args['shares'].get(f'of_co_member[{i}]', 0) or 0)
        args['subscriptions'] = self.signup_manager.subscriptions()
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


def cs_welcome(request, with_sub=False):
    render_dict = {
        'no_subscription': not with_sub
    }
    return render(request, 'welcome.html', render_dict)


@signup_session
def cs_cancel(request, signup_manager):
    signup_manager.clear()
    if request.user.is_authenticated:
        return redirect('subscription-landing')
    else:
        return redirect(Config.organisation_website('url'))
