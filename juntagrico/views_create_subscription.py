from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.forms import *
from juntagrico.models import *
from juntagrico.util import temporal
from juntagrico.decorators import create_subscription_session
from juntagrico.util.form_evaluation import selected_subscription_types
from juntagrico.util.management import *


@create_subscription_session
def cs_select_subscription(request, subscription_session):
    if request.method == 'POST':
        # create dict with subscription type -> selected amount
        selected = selected_subscription_types(request.POST)
        subscription_session.subscriptions = selected
        # select depot (also in edit mode if not previously defined)
        if sum([sub_type.size.units * amount for sub_type, amount in selected.items()]) > 0\
                and not (subscription_session.edit and subscription_session.depot):
            return redirect('cs-depot')
        # edit mode:
        if subscription_session.edit:
            # select start date if not selected
            if not subscription_session.start_date:
                return redirect('cs-start')
            # skip share selection if still enough shares
            if CSSelectSharesView.evaluate_ordered_shares(subscription_session):
                return redirect('cs-summary')
        return redirect('cs-shares')
    render_dict = {
        'selected_subscriptions': subscription_session.subscriptions,
        'hours_used': Config.assignment_unit() == 'HOURS',
        'products': SubscriptionProductDao.get_all(),
    }
    return render(request, 'createsubscription/select_subscription.html', render_dict)


@create_subscription_session
def cs_select_depot(request, subscription_session):
    if request.method == 'POST':
        subscription_session.depot = DepotDao.depot_by_id(request.POST.get('depot'))
        if subscription_session.edit and subscription_session.start_date:  # edit mode: jump to summary
            return redirect('cs-summary')
        return redirect('cs-start')
    depots = DepotDao.all_depots()
    requires_map = True
    for depot in depots:
        requires_map = requires_map or depot.has_geo
    render_dict = {
        'member': subscription_session.main_member,
        'depots': depots,
        'selected': subscription_session.depot,
        'requires_map': requires_map,
    }
    return render(request, 'createsubscription/select_depot.html', render_dict)


@create_subscription_session
def cs_select_start_date(request, subscription_session):
    subscription_form = SubscriptionForm(initial={
        'start_date': subscription_session.start_date or temporal.start_of_next_business_year()
    })
    if request.method == 'POST':
        subscription_form = SubscriptionForm(request.POST)
        if subscription_form.is_valid():
            subscription_session.start_date = subscription_form.cleaned_data['start_date']
            if subscription_session.edit:  # edit mode: jump to summary
                return redirect('cs-summary')
            return redirect('cs-co-members')
    render_dict = {
        'start_date': temporal.start_of_next_business_year(),
        'subscriptionform': subscription_form,
    }
    return render(request, 'createsubscription/select_start_date.html', render_dict)


@create_subscription_session
def cs_add_member(request, subscription_session):
    remove_member = int(request.GET.get('remove', 0))
    if remove_member:
        subscription_session.remove_co_member(remove_member - 1)
        if not CSSelectSharesView.evaluate_ordered_shares(subscription_session):  # recheck shares count
            return redirect('cs-shares')
        return redirect(request.GET.get('source', request.path_info))

    member_exists = False
    member_blocked = False
    # to edit co-members
    edit_member = int(request.GET.get('edit', request.POST.get('edit', 0)))
    # for redirect after editing
    source = request.GET.get('source', request.POST.get('source', request.path_info))
    if request.method == 'POST':
        member_form = RegisterMemberForm(request.POST)
        member = MemberDao.member_by_email(request.POST.get('email'))
        if member is not None:  # use existing member
            member_exists = True
            member_blocked = member.blocked
        elif member_form.is_valid():  # or create new member
            member = Member(**member_form.cleaned_data)
        if member is not None and not member_blocked:
            if edit_member:
                subscription_session.replace_co_member(edit_member - 1, member)
                return redirect(source)
            else:
                subscription_session.add_co_member(member)

    if edit_member:
        member_form = RegisterMemberForm(instance=subscription_session.get_co_member(edit_member - 1))
    else:
        member_form = RegisterMemberForm(initial={
            'addr_street': subscription_session.main_member.addr_street,
            'addr_zipcode': subscription_session.main_member.addr_zipcode,
            'addr_location': subscription_session.main_member.addr_location,
        })
    render_dict = {
        'memberexists': member_exists,
        'memberblocked': member_blocked,
        'memberform': member_form,
        'co_members': subscription_session.co_members,
        'edit_member': edit_member,
        'source': source
    }
    return render(request, 'createsubscription/add_member_cs.html', render_dict)


class CSSelectSharesView(TemplateView):
    template_name = 'createsubscription/select_shares.html'
    share_error = False
    total_shares = 0
    required_shares = 0
    mm_requires_one = False
    session = None

    def get_context_data(self, **kwargs):
        return {
            'share_error': self.share_error,
            'total_shares': self.total_shares,
            'required_shares': self.required_shares,
            'member': self.session.main_member,
            'co_members': self.session.co_members,
            'mm_requires_one': self.mm_requires_one
        }

    @method_decorator(create_subscription_session)
    def dispatch(self, request, subscription_session, *args, **kwargs):
        # if no shares are required: go directly to summary
        if not Config.enable_shares():
            return redirect('cs-summary')
        # initialize
        self.session = subscription_session
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.session.main_member.new_shares = int(request.POST.get('shares_mainmember', 0))
        for co_member in self.session.co_members:
            co_member.new_shares = int(request.POST.get(co_member.email, 0))
        return self.get(request, proceed=True, *args, **kwargs)

    def get(self, request, proceed=False, *args, **kwargs):
        # evaluate number of ordered shares
        success, share_sum, self.total_shares, self.mm_requires_one = \
            self.evaluate_ordered_shares(self.session, get_details=True)
        self.required_shares = max(0, self.total_shares - max(0, share_sum))
        if proceed:
            if success:
                return redirect('cs-summary')
            self.share_error = not success
        return super().get(request, *args, **kwargs)

    @staticmethod
    def evaluate_ordered_shares(subscription_session, get_details=False):
        share_error = False
        share_sum = 0
        total_shares = 0
        mm_requires_one = False
        if Config.enable_shares():  # skip if no shares are needed
            # count current shares
            share_sum = len(subscription_session.main_member.active_shares)
            mm_requires_one = share_sum == 0
            share_sum += sum([len(co_member.active_shares) for co_member in subscription_session.co_members])
            # count new shares
            share_sum += getattr(subscription_session.main_member, 'new_shares', 0) or 0
            share_error |= share_sum == 0 and mm_requires_one
            share_sum += sum([getattr(co_member, 'new_shares', 0) or 0
                              for co_member in subscription_session.co_members])
            # count required shares
            total_shares = sum([sub_type.shares * amount
                                for sub_type, amount in subscription_session.subscriptions.items()])
            # evaluate
            share_error |= share_sum < total_shares
        if get_details:
            return not share_error, share_sum, total_shares, mm_requires_one
        return not share_error


class CSSummaryView(TemplateView):
    template_name = 'createsubscription/summary.html'
    session = None

    def get_context_data(self, **kwargs):
        return self.session.to_dict()

    @method_decorator(create_subscription_session)
    def dispatch(self, request, subscription_session, *args, **kwargs):
        # remember that user reached summary to come back here after editing
        subscription_session.edit = True
        # initialize
        self.session = subscription_session
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        # create subscription
        subscription = None
        if sum(self.session.subscriptions.values()) > 0:
            subscription = create_subscription(self.session.start_date, self.session.depot, self.session.subscriptions)

        # create and/or add members to subscription and create their shares
        create_or_update_member(self.session.main_member, subscription, self.session.main_member.new_shares)
        for co_member in self.session.co_members:
            create_or_update_member(co_member, subscription, co_member.new_shares, self.session.main_member)

        # set primary member of subscription
        if subscription is not None:
            subscription.primary_member = self.session.main_member
            subscription.save()
            send_subscription_created_mail(subscription)

        # finish registration
        return cs_finish(request)


@create_subscription_session
def cs_finish(request, subscription_session, cancelled=False):
    if request.user.is_authenticated:
        subscription_session.clear()
        return redirect('sub-detail')
    elif cancelled:
        subscription_session.clear()
        return redirect('http://'+Config.server_url())
    else:
        # keep session for welcome message
        return redirect('welcome')


@create_subscription_session
def cs_welcome(request, subscription_session):
    render_dict = {
        'no_subscription': subscription_session.main_member.future_subscription is None
    }
    subscription_session.clear()
    return render(request, 'welcome.html', render_dict)
