from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from juntagrico.entity.share import Share
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
