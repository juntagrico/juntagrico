from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.forms import *
from juntagrico.models import *
from juntagrico.util import temporal
from juntagrico.decorators import requires_main_member
from juntagrico.util.form_evaluation import selected_subscription_types
from juntagrico.util.management import *


@requires_main_member
def cs_select_subscription(request, _, multi=False):
    if request.method == 'POST':
        # create dict with subscription type -> selected amount
        selected = selected_subscription_types(request.POST)
        request.session['selected_subscriptions'] = selected
        if sum([sub_type.size.units * amount for sub_type, amount in selected.items()]) > 0:
            return redirect('/my/create/subscription/selectdepot')
        return redirect('/my/create/subscription/shares')
    renderdict = {
        'hours_used': Config.assignment_unit() == 'HOURS',
        'products': SubscriptionProductDao.get_all(),
        'multi_edit': multi and Config.allow_multiple_subscriptions(),
    }
    return render(request, 'createsubscription/select_subscription.html', renderdict)


@requires_main_member
def cs_select_depot(request, main_member):
    if request.method == 'POST':
        depot = DepotDao.depot_by_id(request.POST.get('depot'))
        request.session['selecteddepot'] = depot
        return redirect('/my/create/subscription/start')
    depots = DepotDao.all_depots()
    requires_map = True
    for depot in depots:
        requires_map = requires_map or depot.has_geo
    renderdict = {
        'member': main_member,
        'depots': depots,
        'requires_map': requires_map,
    }
    return render(request, 'createsubscription/select_depot.html', renderdict)


@requires_main_member
def cs_select_start_date(request, _):
    subscriptionform = SubscriptionForm()
    if request.method == 'POST':
        subscriptionform = SubscriptionForm(request.POST)
        if subscriptionform.is_valid():
            request.session['start_date'] = subscriptionform.cleaned_data['start_date']
            return redirect('/my/create/subscription/addmembers')
    renderdict = {
        'start_date': temporal.start_of_next_business_year(),
        'subscriptionform': subscriptionform,
    }
    return render(request, 'createsubscription/select_start_date.html', renderdict)


@requires_main_member
def cs_add_member(request, main_member):
    member_exists = False
    member_blocked = False
    if request.method == 'POST':
        memberform = RegisterMemberForm(request.POST)
        member = MemberDao.member_by_email(request.POST.get('email'))
        if member is not None:  # use existing member
            member_exists = True
            member_blocked = member.blocked
        elif memberform.is_valid():  # or create new member
            member = Member(**memberform.cleaned_data)
        if member is not None:
            request.session['create_co_members'] = request.session.get('create_co_members', []) + [member]

    initial = {'addr_street': main_member.addr_street,
               'addr_zipcode': main_member.addr_zipcode,
               'addr_location': main_member.addr_location,
               }
    memberform = RegisterMemberForm(initial=initial)
    renderdict = {
        'memberexists': member_exists,
        'memberblocked': member_blocked,
        'memberform': memberform,
    }
    return render(request, 'createsubscription/add_member_cs.html', renderdict)


class CSSelectSharesView(TemplateView):
    template_name = 'createsubscription/select_shares.html'
    share_error = False
    total_shares = 0
    required_shares = 0
    mm_requires_one = False
    co_members = []
    main_member = None

    def get_context_data(self, **kwargs):
        return {
            'share_error': self.share_error,
            'total_shares': self.total_shares,
            'required_shares': self.required_shares,
            'member': self.main_member,
            'co_members': self.co_members,
            'has_com_members': len(self.co_members) > 0,
            'mm_requires_one': self.mm_requires_one
        }

    @method_decorator(requires_main_member)
    def dispatch(self, request, main_member, *args, **kwargs):
        # initialize
        self.main_member = main_member
        self.co_members = request.session.get('create_co_members', [])
        # if no shares are required: create subscription directly
        if not Config.enable_shares():
            return self.create_subscription(request)
        # count current shares
        share_sum = len(main_member.active_shares)
        self.mm_requires_one = share_sum == 0
        share_sum += sum([len(co_member.active_shares) for co_member in self.co_members])
        # count required shares
        selected_subscriptions = request.session.get('selected_subscriptions', {})
        self.total_shares = sum([sub_type.shares * amount for sub_type, amount in selected_subscriptions.items()])
        self.required_shares = max(0, self.total_shares - max(0, share_sum))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # evaluate number of ordered shares
        try:
            share_sum = int(request.POST.get('shares_mainmember'))
            self.share_error |= share_sum == 0 and self.mm_requires_one
            share_sum += sum([int(request.POST.get(co_member.email)) for co_member in self.co_members])
            self.share_error |= share_sum < self.required_shares
        except ValueError:
            self.share_error = True
        if not self.share_error:
            return self.create_subscription(request)
        return self.get(request, *args, **kwargs)

    def create_subscription(self, request):
        # create subscription
        subscription = None
        selected_subscriptions = request.session.get('selected_subscriptions', {})
        if selected_subscriptions is not {}:
            start_date = request.session['start_date']
            depot = request.session['selecteddepot']
            subscription = create_subscription(
                start_date, depot, selected_subscriptions)

        # create and/or add members to subscription and create their shares
        create_or_update_member(self.main_member, subscription, int(request.POST.get('shares_mainmember', 0)))
        for co_member in self.co_members:
            create_or_update_member(co_member, subscription,
                                    int(request.POST.get(co_member.email, 0)), self.main_member)

        # set primary member of subscription
        if subscription is not None:
            subscription.primary_member = self.main_member
            subscription.save()
            send_subscription_created_mail(subscription)

        # finish registration
        return cs_finish(request)


def cs_finish(request, cancelled=False):
    request.session['selected_subscription'] = None
    request.session['selecteddepot'] = None
    request.session['start_date'] = None
    request.session['create_co_members'] = []
    if request.user.is_authenticated:
        request.session['main_member'] = None
        return redirect('/my/subscription/detail/')
    elif cancelled:
        request.session['main_member'] = None
        return redirect('http://'+Config.server_url())
    else:
        # keep main_member for welcome message
        return redirect('/my/welcome')


@requires_main_member
def cs_welcome(request, main_member):
    renderdict = {
        'no_subscription': main_member.future_subscription is None
    }
    request.session['main_member'] = None
    return render(request, 'welcome.html', renderdict)
