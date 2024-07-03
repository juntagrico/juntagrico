import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.forms import DateRangeForm
from juntagrico.util import return_to_previous_location, temporal
from juntagrico.util.views_admin import date_from_get
from juntagrico.view_decorators import any_permission_required


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


@method_decorator(any_permission_required('juntagrico.view_share', 'juntagrico.change_share'), name="dispatch")
class ShareCancelledView(ListView):
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


@method_decorator(any_permission_required('juntagrico.view_share', 'juntagrico.change_share'), name="dispatch")
class ShareUnpaidView(ListView):
    template_name = 'juntagrico/manage/share/unpaid.html'

    def get_queryset(self):
        return Share.objects.filter(paid_date__isnull=True).exclude(
            termination_date__lt=datetime.date.today()).order_by('member')


@method_decorator(permission_required('juntagrico.change_subscription'), name="dispatch")
class SubscriptionDepotChangesView(ListView):
    template_name = 'juntagrico/manage/subscription/depot/changes.html'
    queryset = Subscription.objects.exclude(future_depot__isnull=True)


@permission_required('juntagrico.change_subscription')
def subscription_depot_change_confirm(request, subscription_id=None):
    ids = [subscription_id] if subscription_id else request.POST.get('ids').split('_')
    subs = Subscription.objects.filter(id__in=ids)
    subs.activate_future_depots()
    return return_to_previous_location(request)


@method_decorator(
    any_permission_required('juntagrico.view_assignment', 'juntagrico.change_assignment'),
    name="dispatch"
)
class AssignmentsView(DateRangeMixin, ListView):
    template_name = 'juntagrico/manage/assignments.html'

    def get_queryset(self):
        return (
            Subscription.objects.in_date_range(self.start, self.end)
            .annotate_assignments_progress(self.start, self.end)
            .select_related("primary_member")
        )
