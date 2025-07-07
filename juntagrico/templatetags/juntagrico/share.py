from django import template
from django.utils.translation import gettext as _
from schwifty import IBAN

register = template.Library()


@register.simple_tag
def required_for_subscription(share, index):
    member = share.member
    subscription = member.subscription_future or member.subscription_current
    if subscription:
        remaining = subscription.required_shares - subscription.paid_shares
        if index <= remaining:
            other_unpaid = subscription.co_members(of_member=member).filter(
                share__isnull=False, share__paid_date__isnull=True, share__cancelled_date__isnull=True
            )
            if index > remaining - other_unpaid.count():
                return _("Ja. Oder ") + ", ".join(
                    str(o) for o in other_unpaid.distinct()
                ) + ". " + _("({} insgesamt)").format(remaining)
            return _("Ja")
    return _("Nein")


@register.filter
def clean_iban(iban_str):
    iban = IBAN(iban_str, allow_invalid=True)
    if iban.is_valid:
        return str(iban)
    return iban_str
