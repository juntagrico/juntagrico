import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.member import Member
from juntagrico.entity.member import SubscriptionMembership
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.forms import DateRangeForm
from juntagrico.util import return_to_previous_location, temporal
from juntagrico.util.auth import MultiplePermissionsRequiredMixin
from juntagrico.util.views_admin import date_from_get


class DateRangeMixin:
    """
    View mixin
    Adds a DateRangeForm to the context with start and end as follows:
    * `start` and `end` arguments passed directly into as_view() method in urls.py
    * GET variables `start_date` and `end_date`
    * Business year containing the GET variable `ref_date`, defaults to today
    """
    start = None
    end = None

    def __init__(self, start=None, end=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.ref_date = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.ref_date = date_from_get(request, 'ref_date')
        self.start = self.start or date_from_get(request, 'start_date') or self.get_default_start()
        self.end = self.end or date_from_get(request, 'end_date') or self.get_default_end()

    def get_default_start(self):
        return temporal.start_of_specific_business_year(self.ref_date)

    def get_default_end(self):
        return temporal.end_of_specific_business_year(self.ref_date)

    def get_context_data(self, **kwargs):
        if "date_form" not in kwargs:
            kwargs["date_form"] = self.get_form()
        return super().get_context_data(**kwargs)

    def get_form(self):
        return DateRangeForm(initial={'start_date': self.start, 'end_date': self.end})


class TitledListView(ListView):
    title = _('Titel')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class MemberView(MultiplePermissionsRequiredMixin, TitledListView):
    permission_required = [['juntagrico.view_member', 'juntagrico.change_member',
                            'juntagrico.can_filter_members']]
    template_name = 'juntagrico/manage/member/show.html'
    queryset = Member.objects.all
    title = _('Alle {}').format(Config.vocabulary('member_pl'))

    def get_queryset(self):
        return super().get_queryset()().prefetch_for_list


class MemberActiveView(MemberView):
    queryset = Member.objects.active
    title = _('Alle aktiven {}').format(Config.vocabulary('member_pl'))


class AreaMemberView(MemberView):
    permission_required = 'juntagrico.is_area_admin'
    title = _('Alle aktiven {member} im Tätigkeitsbereich {area_name}').format(
        member=Config.vocabulary('member_pl'), area_name='{area_name}'
    )

    def get_queryset(self):
        self.area = get_object_or_404(
            ActivityArea,
            id=int(self.kwargs['area_id']),
            coordinator=self.request.user.member
        )
        return self.area.members.active().prefetch_for_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title.format(area_name=self.area.name)
        context['mail_url'] = 'mail-area'
        context['hide_areas'] = True
        return context


class MemberCanceledView(MultiplePermissionsRequiredMixin, ListView):
    permission_required = [['juntagrico.view_member', 'juntagrico.change_member']]
    template_name = 'juntagrico/manage/member/canceled.html'
    queryset = Member.objects.canceled


@permission_required('juntagrico.change_member')
def member_deactivate(request, member_id=None):
    change_date = request.session.get('changedate', None)
    if member_id:
        members = [get_object_or_404(Member, id=member_id)]
    else:
        members = Member.objects.filter(id__in=request.POST.get('member_ids').split('_'))
    for member in members:
        member.deactivate(change_date)
    return return_to_previous_location(request)


class ShareCanceledView(MultiplePermissionsRequiredMixin, ListView):
    permission_required = [['juntagrico.view_share', 'juntagrico.change_share']]
    template_name = 'juntagrico/manage/share/canceled.html'
    queryset = Share.objects.canceled().annotate_backpayable


@permission_required('juntagrico.change_share')
def share_payout(request, share_id=None):
    change_date = request.session.get('changedate', None)
    if share_id:
        shares = [get_object_or_404(Share, id=share_id)]
    else:
        shares = Share.objects.filter(id__in=request.POST.get('share_ids').split('_'))
    for share in shares:
        # TODO: capture validation errors and display them. Continue with other shares
        share.payback(change_date)
    return return_to_previous_location(request)


class ShareUnpaidView(MultiplePermissionsRequiredMixin, ListView):
    permission_required = [['juntagrico.view_share', 'juntagrico.change_share']]
    template_name = 'juntagrico/manage/share/unpaid.html'

    def get_queryset(self):
        return (
            Share.objects.filter(paid_date__isnull=True)
            .exclude(termination_date__lt=datetime.date.today())
            .order_by('member')
        )


class SubscriptionView(MultiplePermissionsRequiredMixin, TitledListView):
    permission_required = [['juntagrico.view_subscription', 'juntagrico.change_subscription',
                            'juntagrico.can_filter_subscriptions']]
    template_name = 'juntagrico/manage/subscription/show.html'
    queryset = Subscription.objects.active
    title = _('Alle aktiven {} im Überblick').format(Config.vocabulary('subscription_pl'))


class SubscriptionRecentView(MultiplePermissionsRequiredMixin, DateRangeMixin, TemplateView):
    permission_required = [['juntagrico.view_subscription', 'juntagrico.change_subscription',
                            'juntagrico.can_filter_subscriptions']]
    template_name = 'juntagrico/manage/subscription/recent.html'

    def get_default_start(self):
        return datetime.date.today() - datetime.timedelta(days=30)

    def get_default_end(self):
        return datetime.date.today()

    def get_context_data(self, **kwargs):
        date_range = (self.start, self.end)
        kwargs.update(dict(
            ordered_parts=SubscriptionPart.objects.filter(creation_date__range=date_range),
            activated_parts=SubscriptionPart.objects.filter(activation_date__range=date_range),
            cancelled_parts=SubscriptionPart.objects.filter(cancellation_date__range=date_range),
            deactivated_parts=SubscriptionPart.objects.filter(deactivation_date__range=date_range),
            joined_memberships=SubscriptionMembership.objects.filter(join_date__range=date_range),
            left_memberships=SubscriptionMembership.objects.filter(leave_date__range=date_range),
        ))
        return super().get_context_data(**kwargs)


class SubscriptionPendingView(PermissionRequiredMixin, ListView):
    permission_required = ['juntagrico.change_subscription']
    template_name = 'juntagrico/manage/subscription/pending.html'

    def get_queryset(self):
        return Subscription.objects.filter(
                Q(parts__activation_date=None)
                | Q(parts__cancellation_date__isnull=False, parts__deactivation_date=None)
            ).prefetch_related('parts').distinct()


@permission_required('juntagrico.change_subscriptionpart')
def parts_apply(request):
    parts = SubscriptionPart.objects.filter(id__in=request.POST.getlist('parts[]'))
    change_date = request.session.get('changedate', None)
    with transaction.atomic():
        for part in parts:
            if part.activation_date is None and part.deactivation_date is None:
                if part.subscription.activation_date is None:
                    # automatically activate subscription, but don't activate all parts
                    part.subscription.__skip_part_activation__ = True
                    part.subscription.activate(change_date)
                part.activate(change_date)
            if part.cancellation_date is not None:
                part.deactivate(change_date)
                # deactivate entire subscription, if this was the last part
                if not part.subscription.parts.waiting_or_active(change_date).exists():
                    part.subscription.deactivate(change_date)
    return return_to_previous_location(request)


class DepotSubscriptionView(SubscriptionView):
    permission_required = 'juntagrico.is_depot_admin'
    title = _('Alle aktiven {subs} im {depot} {depot_name}').format(
        subs=Config.vocabulary('subscription_pl'), depot=Config.vocabulary('depot'), depot_name='{depot_name}'
    )

    def get_queryset(self):
        self.depot = get_object_or_404(Depot, id=int(self.kwargs['depot_id']), contact=self.request.user.member)
        return super().get_queryset()().filter(depot=self.depot)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title.format(depot_name=self.depot.name)
        context['mail_url'] = 'mail-depot'
        return context


class SubscriptionDepotChangesView(PermissionRequiredMixin, ListView):
    permission_required = 'juntagrico.change_subscription'
    template_name = 'juntagrico/manage/subscription/depot/changes.html'
    queryset = Subscription.objects.exclude(future_depot__isnull=True)


@permission_required('juntagrico.change_subscription')
def subscription_depot_change_confirm(request, subscription_id=None):
    ids = [subscription_id] if subscription_id else request.POST.get('ids').split('_')
    subs = Subscription.objects.filter(id__in=ids)
    subs.activate_future_depots()
    return return_to_previous_location(request)


@permission_required('juntagrico.change_subscription')
def subscription_inconsistencies(request):
    management_list = []
    for sub in Subscription.objects.all():
        try:
            sub.clean()
            for part in sub.parts.all():
                part.clean()
            for member in sub.subscriptionmembership_set.all():
                member.clean()
        except Exception as e:
            management_list.append({'subscription': sub, 'error': e})
        if sub.primary_member is None:
            management_list.append({'subscription': sub, 'error': _('HauptbezieherIn ist nicht gesetzt')})
    render_dict = {
        'object_list': management_list,
    }
    return render(request, 'juntagrico/manage/subscription/inconsistent.html', render_dict)


class AssignmentsView(MultiplePermissionsRequiredMixin, DateRangeMixin, ListView):
    permission_required = [['juntagrico.view_assignment', 'juntagrico.change_assignment']]
    template_name = 'juntagrico/manage/assignments.html'

    def get_queryset(self):
        return (
            Subscription.objects.in_date_range(self.start, self.end)
            .annotate_assignments_progress(self.start, self.end)
            .select_related("primary_member")
        )
