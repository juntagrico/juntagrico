from django import template
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.translation import gettext as _

register = template.Library()


@register.simple_tag
def required_for_subscription(share, index):
    member = share.member
    subscription = member.subscription_future or member.subscription_current
    if subscription:
        remaining = subscription.required_shares - subscription.paid_shares
        if index <= remaining:
            other_unpaid = subscription.recipients_qs.exclude(member=member).filter(
                member__share__isnull=False, member__share__paid_date__isnull=True
            ).annotate(
                member_name=Concat('member__first_name', Value(' '), 'member__last_name')
            ).values('member_name')
            if index > remaining - other_unpaid.count():
                return _("Ja. Oder ") + ", ".join(
                    o['member_name'] for o in other_unpaid.distinct()
                ) + ". " + _("({} insgesamt)").format(remaining)
            return _("Ja")
    return _("Nein")
