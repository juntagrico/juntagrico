import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.util import return_to_previous_location
from juntagrico.view_decorators import any_permission_required


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
