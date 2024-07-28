import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
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

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        ref_date = date_from_get(request, 'ref_date')
        self.start = self.start or date_from_get(request, 'start_date') or temporal.start_of_specific_business_year(ref_date)
        self.end = self.end or date_from_get(request, 'end_date') or temporal.end_of_specific_business_year(ref_date)

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


class MemberCancelledView(MultiplePermissionsRequiredMixin, ListView):
    permission_required = [['juntagrico.view_member', 'juntagrico.change_member']]
    template_name = 'juntagrico/manage/member/cancelled.html'
    queryset = Member.objects.cancelled


@permission_required('juntagrico.change_member')
def member_deactivate(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.deactivation_date = datetime.date.today()
    member.save()
    return return_to_previous_location(request)


class ShareCancelledView(MultiplePermissionsRequiredMixin, ListView):
    permission_required = [['juntagrico.view_share', 'juntagrico.change_share']]
    template_name = 'juntagrico/manage/share/cancelled.html'
    queryset = Share.objects.cancelled().annotate_backpayable


@permission_required('juntagrico.change_share')
def share_payout(request, share_id=None):
    if share_id:
        shares = [get_object_or_404(Share, id=share_id)]
    else:
        shares = Share.objects.filter(id__in=request.POST.get('share_ids').split('_'))
    for share in shares:
        # TODO: capture validation errors and display them. Continue with other shares
        share.payback()
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


class AssignmentsView(MultiplePermissionsRequiredMixin, DateRangeMixin, ListView):
    permission_required = [['juntagrico.view_assignment', 'juntagrico.change_assignment']]
    template_name = 'juntagrico/manage/assignments.html'

    def get_queryset(self):
        return (
            Subscription.objects.in_date_range(self.start, self.end)
            .annotate_assignments_progress(self.start, self.end)
            .select_related("primary_member")
        )
