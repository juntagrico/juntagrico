import pkg_resources

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.utils import timezone
from django.template import loader

from juntagrico.config import Config
from juntagrico.dao.sharedao import ShareDao


@permission_required('juntagrico.is_operations_group')
def share_pain001(request):
    now = timezone.now()
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename = "share_pain'+now.strftime('%y_%m_%d_%H_%M')+'.xml"'
    t = loader.get_template('iso20022/share_pain.001.xml')
    shares = ShareDao.canceled_shares()
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
