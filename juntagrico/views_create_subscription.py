from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import ModelFormMixin

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.forms import SubscriptionForm, EditCoMemberForm, RegisterMultiCoMemberForm, \
    RegisterFirstMultiCoMemberForm, SubscriptionPartSelectForm, RegisterSummaryForm
from juntagrico.util import temporal
from juntagrico.util.management import new_signup
from juntagrico.view_decorators import create_subscription_session


@create_subscription_session
def cs_select_subscription(request, cs_session):
    if request.method == 'POST':
        form = SubscriptionPartSelectForm(cs_session.subscriptions, request.POST)
        if form.is_valid():
            cs_session.subscriptions = form.get_selected()
            return redirect(cs_session.next_page())
    else:
        form = SubscriptionPartSelectForm(cs_session.subscriptions)

    render_dict = {
        'form': form,
        'subscription_selected': sum(form.get_selected().values()) > 0,
        'hours_used': Config.assignment_unit() == 'HOURS',
    }
    return render(request, 'createsubscription/select_subscription.html', render_dict)


@create_subscription_session
def cs_select_depot(request, cs_session):
    if request.method == 'POST':
        cs_session.depot = DepotDao.depot_by_id(request.POST.get('depot'))
        return redirect(cs_session.next_page())

    depots = DepotDao.all_visible_depots()
    requires_map = any(depot.has_geo for depot in depots)
    render_dict = {
        'member': cs_session.main_member,
        'depots': depots,
        'selected': cs_session.depot,
        'requires_map': requires_map,
    }
    return render(request, 'createsubscription/select_depot.html', render_dict)


@create_subscription_session
def cs_select_start_date(request, cs_session):
    subscription_form = SubscriptionForm(initial={
        'start_date': cs_session.start_date or temporal.start_of_next_business_year()
    })
    if request.method == 'POST':
        subscription_form = SubscriptionForm(request.POST)
        if subscription_form.is_valid():
            cs_session.start_date = subscription_form.cleaned_data['start_date']
            return redirect(cs_session.next_page())
    render_dict = {
        'start_date': temporal.start_of_next_business_year(),
        'subscriptionform': subscription_form,
    }
    return render(request, 'createsubscription/select_start_date.html', render_dict)


class CSAddMemberView(FormView, ModelFormMixin):
    template_name = 'createsubscription/add_member_cs.html'

    def __init__(self):
        super().__init__()
        self.cs_session = None
        self.object = None
        self.edit = False
        self.existing_emails = []

    def get_form_class(self):
        return EditCoMemberForm if self.edit else \
            RegisterMultiCoMemberForm if self.cs_session.co_members else RegisterFirstMultiCoMemberForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['existing_emails'] = self.existing_emails
        return form_kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{},
            co_members=self.cs_session.co_members if not self.edit else [],
            **kwargs
        )

    def get_initial(self):
        # use address from main member as default
        mm = self.cs_session.main_member
        return {
            'addr_street': mm.addr_street,
            'addr_zipcode': mm.addr_zipcode,
            'addr_location': mm.addr_location,
            'edit': self.edit
        }

    @method_decorator(create_subscription_session)
    def dispatch(self, request, cs_session, *args, **kwargs):
        self.cs_session = cs_session
        self.edit = int(request.GET.get('edit', request.POST.get('edit', 0)))
        # function: edit co-member from list
        if self.edit:
            self.object = self.cs_session.get_co_member(self.edit - 1)

        # collect used email addresses to block reusage
        self.existing_emails.append(cs_session.main_member.email.lower())
        for co_member in self.cs_session.co_members:
            if co_member is not self.object:
                self.existing_emails.append(co_member.email.lower())

        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        if form.existing_member:  # use existing member if found
            return self.form_valid(form)
        return super().form_invalid(form)

    def form_valid(self, form):
        # create new member from form data
        return self._add_or_replace_co_member(form.existing_member or form.instance)

    def _add_or_replace_co_member(self, member):
        if self.edit:
            return redirect(self.cs_session.next_page())
        else:
            self.cs_session.add_co_member(member)
            return redirect('.')

    def get(self, request, *args, **kwargs):
        # done: move to next page
        if request.GET.get('next') is not None:
            self.cs_session.co_members_done = True
            return redirect(self.cs_session.next_page())

        # function: remove co-members from list
        remove_member = int(request.GET.get('remove', 0))
        if remove_member:
            self.cs_session.remove_co_member(remove_member - 1)
            return redirect(self.cs_session.next_page())

        # render page
        return super().get(request, *args, **kwargs)


class CSSelectSharesView(TemplateView):
    template_name = 'createsubscription/select_shares.html'

    def __init__(self):
        super().__init__()
        self.cs_session = None

    def get_context_data(self, shares, **kwargs):
        return super().get_context_data(
            **{},
            **{
                'shares': shares,
                'member': self.cs_session.main_member,
                'co_members': self.cs_session.co_members
            },
            **kwargs
        )

    @method_decorator(create_subscription_session)
    def dispatch(self, request, cs_session, *args, **kwargs):
        self.cs_session = cs_session
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # read form
        self.cs_session.main_member.new_shares = int(request.POST.get('shares_mainmember', 0) or 0)
        for co_member in self.cs_session.co_members:
            co_member.new_shares = int(request.POST.get(co_member.email, 0) or 0)
        # evaluate
        shares = self.cs_session.count_shares()
        if self.cs_session.evaluate_ordered_shares(shares):
            return redirect('cs-summary')
        # show error otherwise
        shares['error'] = True
        return super().get(request, *args, shares=shares, **kwargs)

    def get(self, request, *args, **kwargs):
        # evaluate number of ordered shares
        shares = self.cs_session.count_shares()
        return super().get(request, *args, shares=shares, **kwargs)


class CSSummaryView(FormView):
    template_name = 'createsubscription/summary.html'
    form_class = RegisterSummaryForm

    def __init__(self):
        super().__init__()
        self.cs_session = None

    def get_initial(self):
        return {'comment': getattr(self.cs_session.main_member, 'comment', '')}

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{},
            **self.cs_session.to_dict(),
            **kwargs
        )

    @method_decorator(create_subscription_session)
    def dispatch(self, request, cs_session, *args, **kwargs):
        self.cs_session = cs_session
        # remember that user reached summary to come back here after editing
        cs_session.edit = True
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.cs_session.main_member.comment = form.cleaned_data["comment"]
        # handle new signup
        member = new_signup(self.cs_session.pop())
        # finish registration
        if member.subscription_future is None:
            return redirect('welcome')
        return redirect('welcome-with-sub')


def cs_welcome(request, with_sub=False):
    render_dict = {
        'no_subscription': not with_sub
    }
    return render(request, 'welcome.html', render_dict)


@create_subscription_session
def cs_cancel(request, cs_session):
    cs_session.clear()
    if request.user.is_authenticated:
        return redirect('sub-detail')
    else:
        return redirect('http://' + Config.server_url())
