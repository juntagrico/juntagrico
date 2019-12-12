from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.entity.share import Share


@permission_required('juntagrico.is_operations_group')
def share_pain001(request):
    if request.method != 'POST':
        raise Http404
    now = timezone.now()
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename = "share_pain' + now.strftime('%y_%m_%d_%H_%M') + '.xml"'
    t = loader.get_template('iso20022/share_pain.001.xml')
    share_ids = request.POST.get('share_ids').split('_')
    shares = [get_object_or_404(Share, id=int(sid)) for sid in share_ids]
    payable_shares = [share for share in shares if share.member.iban is not None and share.member.iban != '']
    context = {
        'shares': payable_shares,
        'nmbr_of_tx': len(payable_shares),
        'amount': Config.share_price(),
        'total_amount': len(payable_shares) * int(Config.share_price()),
        'banking_info': Config.organisation_bank_connection(),
        'version': '1.1.8',
        'now': now,
        'name': Config.organisation_long_name(),
    }
    response.write(t.render(context))
    return response
