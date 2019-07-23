from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.share import Share
from juntagrico.signals import share_created
from juntagrico.util.bills import bill_share


def share_post_save(sender, instance, created, **kwargs):
    share_created.send(sender=sender, instance=instance, created=created)
    check_share_consistency(instance)


def handle_share_created(sender, instance, created, **kwargs):
    if created and Config.billing():
        bill_share(instance)


def check_share_consistency(instance: Share):
    is_paid = instance.paid_date is not None
    is_canceled = instance.cancelled_date is not None
    is_terminated = instance.termination_date is not None
    is_payed_back = instance.payback_date is not None
    if (is_canceled or is_terminated or is_payed_back) and not is_paid:
        raise ValidationError(_('Bitte "Bezahlt am" ausfüllen'), code='invalid')
    if (is_terminated or is_payed_back) and not is_canceled:
        raise ValidationError(_('Bitte "Gekündigt am" ausfüllen'), code='invalid')
    if is_payed_back and not is_terminated:
        raise ValidationError(_('Bitte "Gekündigt auf" ausfüllen'), code='invalid')
    if not(instance.paid_date <= instance.cancelled_date <= instance.termination_date <= instance.payback_date):
        raise ValidationError(_('Daten Reihenfolge stimm nicht.'), code='invalid')
