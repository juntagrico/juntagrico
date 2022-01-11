from datetime import date

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import FormView
from django.views.generic.edit import ModelFormMixin

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.forms import RegisterMemberForm, EditMemberForm, AddCoMemberForm, SubscriptionPartOrderForm, \
    NicknameForm
from juntagrico.mailer import membernotification, adminnotification
from juntagrico.util import addons
from juntagrico.util import temporal, return_to_previous_location
from juntagrico.util.management import cancel_sub, create_subscription_parts
from juntagrico.util.management import create_or_update_co_member, create_share
from juntagrico.util.pdf import render_to_pdf_http
from juntagrico.util.temporal import end_of_next_business_year, next_cancelation_date, end_of_business_year, \
    cancelation_date
from juntagrico.view_decorators import primary_member_of_subscription, create_subscription_session


@login_required
def subscription(request, subscription_id=None):
    '''
    Details for an subscription of a member
    '''
    member = request.user.member
    future_subscription = member.subscription_future is not None
    if subscription_id is None:
        subscription = member.subscription_current
    else:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        future_subscription = future_subscription and not(
            subscription == member.subscription_future)
    end_date = end_of_next_business_year()
    renderdict = {}
    if subscription is not None:
        cancellation_date = subscription.cancellation_date
        if cancellation_date is not None and cancellation_date <= next_cancelation_date():
            end_date = end_of_business_year()
        asc = member.usable_shares_count
        share_error = subscription.share_overflow - asc < 0
        primary = subscription.primary_member.id == member.id
        can_leave = member.is_cooperation_member and not share_error and not primary
        renderdict.update({
            'subscription': subscription,
            'co_members': subscription.co_members(member),
            'primary': subscription.primary_member.email == member.email,
            'next_size_date': Subscription.next_size_change_date(),
            'has_extra_subscriptions': SubscriptionProductDao.all_extra_products().count() > 0,
            'sub_overview_addons': addons.config.get_sub_overviews(),
            'can_leave': can_leave,
        })
    renderdict.update({
        'no_subscription': subscription is None,
        'end_date': end_date,
        'can_order': member.can_order_subscription,
        'future_subscription': future_subscription,
        'member': request.user.member,
        'shares': request.user.member.active_shares.count(),
        'shares_unpaid': request.user.member.share_set.filter(paid_date=None).count(),
    })
    return render(request, 'subscription.html', renderdict)


@primary_member_of_subscription
def subscription_change(request, subscription_id):
    '''
    change an subscription
    '''
    subscription = get_object_or_404(Subscription, id=subscription_id)
    renderdict = {
        'subscription': subscription,
        'member': request.user.member,
        'next_cancel_date': temporal.next_cancelation_date(),
        'next_business_year': temporal.start_of_next_business_year(),
        'sub_change_addons': addons.config.get_sub_changes(),
    }
    return render(request, 'subscription_change.html', renderdict)


@primary_member_of_subscription
def depot_change(request, subscription_id):
    '''
    change a depot
    '''
    subscription = get_object_or_404(Subscription, id=subscription_id)
    saved = False
    if request.method == 'POST':
        if subscription.state == 'waiting':
            subscription.depot = get_object_or_404(
                Depot, id=int(request.POST.get('depot')))
        else:
            subscription.future_depot = get_object_or_404(
                Depot, id=int(request.POST.get('depot')))
        subscription.save()
        saved = True
    depots = DepotDao.all_visible_depots()
    requires_map = False
    for depot in depots:
        requires_map = requires_map or depot.has_geo
    renderdict = {
        'subscription': subscription,
        'saved': saved,
        'member': request.user.member,
        'depots': depots,
        'requires_map': requires_map,
    }
    return render(request, 'depot_change.html', renderdict)


@primary_member_of_subscription
def primary_change(request, subscription_id):
    '''
    change primary member
    '''
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        new_primary = get_object_or_404(Member, id=int(request.POST.get('primary')))
        subscription.primary_member = new_primary
        subscription.save()
        return redirect('sub-detail-id', subscription_id=subscription.id)
    if Config.enable_shares():
        co_members = [m for m in subscription.other_recipients() if m.is_cooperation_member]
    else:
        co_members = subscription.other_recipients()
    renderdict = {
        'subscription': subscription,
        'co_members': co_members,
        'has_comembers': len(co_members) > 0
    }
    return render(request, 'pm_change.html', renderdict)


@primary_member_of_subscription
def size_change(request, subscription_id):
    """
    change the size of a subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    parts_order_allowed = subscription.waiting or subscription.active
    if request.method == 'POST':
        if not parts_order_allowed:
            raise ValidationError(_('Für gekündigte {} können keine Bestandteile bestellt werden').
                                  format(Config.vocabulary('subscription_pl')), code='invalid')
        form = SubscriptionPartOrderForm(subscription, request.POST)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return return_to_previous_location(request)
    else:
        form = SubscriptionPartOrderForm()
    renderdict = {
        'form': form,
        'subscription': subscription,
        'hours_used': Config.assignment_unit() == 'HOURS',
        'next_cancel_date': temporal.next_cancelation_date(),
        'parts_order_allowed': parts_order_allowed,
    }
    return render(request, 'size_change.html', renderdict)


@primary_member_of_subscription
def extra_change(request, subscription_id):
    """
        change an extra subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    extra_order_allowed = subscription.waiting or subscription.active
    if request.method == 'POST':
        if not extra_order_allowed:
            raise ValidationError(_('Für gekündigte {} können keine Zusatzabos bestellt werden').
                                  format(Config.vocabulary('subscription_pl')), code='invalid')
        form = SubscriptionPartOrderForm(subscription, request.POST,
                                         product_method=SubscriptionProductDao.all_visible_extra_products)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return return_to_previous_location(request)
    else:
        form = SubscriptionPartOrderForm(product_method=SubscriptionProductDao.all_visible_extra_products)
    renderdict = {
        'form': form,
        'extras': subscription.active_and_future_extra_subscriptions.all(),
        'subscription': subscription,
        'sub_id': subscription_id,
        'extra_order_allowed': extra_order_allowed,
    }
    return render(request, 'extra_change.html', renderdict)


class SignupView(FormView, ModelFormMixin):
    template_name = 'signup.html'

    def __init__(self):
        super().__init__()
        self.cs_session = None
        self.object = None

    def get_form_class(self):
        return EditMemberForm if self.cs_session.edit else RegisterMemberForm

    @method_decorator(create_subscription_session)
    def dispatch(self, request, cs_session, *args, **kwargs):
        if Config.enable_registration() is False:
            raise Http404
        # logout if existing user is logged in
        if request.user.is_authenticated:
            logout(request)
            cs_session.clear()  # empty session object

        self.cs_session = cs_session
        self.object = self.cs_session.main_member
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.cs_session.main_member = form.instance
        # monkey patch comment field into main_member
        self.cs_session.main_member.comment = form.cleaned_data.get('comment', '')
        return redirect(self.cs_session.next_page())


def confirm(request, member_hash):
    """
    Confirm from a user that has been added as a co_subscription member
    """

    for member in MemberDao.all_members().filter(confirmed=False):
        if member_hash == member.get_hash():
            member.confirmed = True
            member.save()

    return redirect('home')


class AddCoMemberView(FormView, ModelFormMixin):
    template_name = 'add_member.html'
    form_class = AddCoMemberForm

    def __init__(self):
        super().__init__()
        self.object = None
        self.subscription = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{},
            **kwargs
        )

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['existing_emails'] = [m.email.lower() for m in self.subscription.recipients]
        return form_kwargs

    def get_initial(self):
        # use address from main member as default
        mm = self.request.user.member
        return {
            'addr_street': mm.addr_street,
            'addr_zipcode': mm.addr_zipcode,
            'addr_location': mm.addr_location
        }

    @method_decorator(primary_member_of_subscription)
    def dispatch(self, request, subscription_id, *args, **kwargs):
        self.subscription = get_object_or_404(Subscription, id=subscription_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # add existing member
        co_member = getattr(form, 'existing_member', None)
        shares = 0
        # or create new member and order shares for them
        if co_member is None:
            shares = form.cleaned_data['shares']
            co_member = form.instance
        create_or_update_co_member(co_member, self.subscription, shares)
        return self._done()

    def _done(self):
        return redirect('sub-detail-id', subscription_id=self.subscription.id)


def error_page(request, error_message):
    renderdict = {'error_message': error_message}
    return render(request, 'error.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def activate_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    change_date = request.session.get('changedate', None)
    try:
        subscription.activate(change_date)
    except ValidationError as e:
        return error_page(request, e.message)
    return return_to_previous_location(request)


@permission_required('juntagrico.is_operations_group')
def deactivate_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    change_date = request.session.get('changedate', None)
    try:
        subscription.deactivate(change_date)
    except ValidationError as e:
        return error_page(request, e.message)
    return return_to_previous_location(request)


@primary_member_of_subscription
def cancel_part(request, part_id, subscription_id):
    part = get_object_or_404(SubscriptionPart, subscription__id=subscription_id, id=part_id)
    if part.activation_date is None:
        part.delete()
    else:
        part.cancel()
        adminnotification.subpart_canceled(part)
    return return_to_previous_location(request)


@primary_member_of_subscription
def cancel_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    now = timezone.now().date()
    end_date = end_of_business_year() if now <= cancelation_date() else end_of_next_business_year()
    if request.method == 'POST':
        cancel_sub(subscription, request.POST.get('end_date'), request.POST.get('message'))
        return redirect('sub-detail')
    renderdict = {
        'end_date': end_date,
    }
    return render(request, 'cancelsubscription.html', renderdict)


@login_required
def leave_subscription(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    member = request.user.member
    asc = member.usable_shares_count
    share_error = subscription.share_overflow - asc < 0
    primary = subscription.primary_member.id == member.id
    can_leave = member.is_cooperation_member and not share_error and not primary
    if not can_leave:
        return redirect('sub-detail')
    if request.method == 'POST':
        member.leave_subscription(subscription)
        primary_member = subscription.primary_member
        membernotification.co_member_left_subscription(primary_member, member, request.POST.get('message'))
        return redirect('home')
    return render(request, 'leavesubscription.html', {})


@permission_required('juntagrico.change_subscriptionpart')
def activate_part(request, part_id):
    part = get_object_or_404(SubscriptionPart, id=part_id)
    change_date = request.session.get('changedate', None)
    if part.activation_date is None and part.deactivation_date is None:
        part.activate(change_date)
    return return_to_previous_location(request)


@permission_required('juntagrico.change_subscriptionpart')
def deactivate_part(request, part_id):
    part = get_object_or_404(SubscriptionPart, id=part_id)
    change_date = request.session.get('changedate', None)
    if part.activation_date is not None:
        part.deactivate(change_date)
    return return_to_previous_location(request)


@primary_member_of_subscription
def change_nickname(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        if form.is_valid():
            subscription.nickname = form.cleaned_data['nickname']
            subscription.save()
            return redirect('sub-detail-id', subscription_id=subscription_id)
    else:
        form = NicknameForm()
    renderdict = {
        'form': form,
    }
    return render(request, 'change_nickname.html', renderdict)


@login_required
def manage_shares(request):
    if request.method == 'POST':
        try:
            ordered_shares = int(request.POST.get('shares'))
            shareerror = ordered_shares < 1
        except ValueError:
            shareerror = True
        if not shareerror:
            create_share(request.user.member, ordered_shares)
            return redirect(reverse('manage-shares'))
    else:
        shareerror = False
    member = request.user.member
    shares = member.share_set.order_by('cancelled_date', '-paid_date')

    active_share_years = member.active_share_years
    if active_share_years:
        active_share_years.remove(timezone.now().year)
    renderdict = {
        'shares': shares.all(),
        'shareerror': shareerror,
        'required': member.required_shares_count,
        'certificate_years': active_share_years,
    }
    return render(request, 'manage_shares.html', renderdict)


@login_required
def share_certificate(request):
    year = int(request.GET['year'])
    member = request.user.member
    active_share_years = member.active_share_years
    if year >= timezone.now().year or year not in active_share_years:
        return error_page(request, _('{}-Bescheinigungen können nur für vergangene Jahre ausgestellt werden.').format(Config.vocabulary('share')))
    shares_date = date(year, 12, 31)
    shares = member.active_shares_for_date(date=shares_date).values('value').annotate(count=Count('value')).annotate(total=Sum('value')).order_by('value')
    shares_total = 0
    for share in shares:
        shares_total = shares_total + share['total']
    renderdict = {
        'member': member,
        'cert_date': timezone.now().date(),
        'shares_date': shares_date,
        'shares': shares,
        'shares_total': shares_total,
    }
    return render_to_pdf_http('exports/share_certificate.html', renderdict, _('Bescheinigung') + str(year) + '.pdf')


@login_required
def cancel_share(request, share_id):
    member = request.user.member
    if member.cancellable_shares_count > 0:
        share = get_object_or_404(Share, id=share_id, member=member)
        share.cancelled_date = timezone.now().date()
        share.save()
    return return_to_previous_location(request)


@permission_required('juntagrico.is_operations_group')
def payout_share(request, share_id):
    share = get_object_or_404(Share, id=share_id)
    share.payback_date = timezone.now().date()
    share.save()
    member = share.member
    if member.active_shares_count == 0 and member.canceled is True:
        member.deactivation_date = timezone.now().date()
        member.save()
    return return_to_previous_location(request)
