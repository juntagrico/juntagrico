import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.mailer import adminnotification
from juntagrico.signals import share_created


def share_pre_save(sender, instance, **kwargs):
    check_share_consistency(instance)


def share_post_save(sender, instance, created, **kwargs):
    if created:
        share_created.send(sender=sender, instance=instance)


def handle_share_created(sender, instance, **kwargs):
    adminnotification.share_created(instance)


def check_share_consistency(instance):
    is_paid = instance.paid_date is not None
    is_canceled = instance.cancelled_date is not None
    is_terminated = instance.termination_date is not None
    is_payed_back = instance.payback_date is not None
    paid_date = instance.paid_date or instance.cancelled_date or datetime.date.today()
    canceled_date = instance.cancelled_date or paid_date
    termination_date = instance.termination_date or canceled_date
    payback_date = instance.payback_date or termination_date
    if is_payed_back and not is_paid:
        raise ValidationError(_('Bitte "Bezahlt am" ausfüllen'), code='missing_paid_date')
    if (is_terminated or is_payed_back) and not is_canceled:
        raise ValidationError(_('Bitte "Gekündigt am" ausfüllen'), code='missing_cancellation_date')
    if is_payed_back and not is_terminated:
        raise ValidationError(_('Bitte "Gekündigt auf" ausfüllen'), code='missing_termination_date')
    if not (paid_date <= canceled_date <= termination_date <= payback_date):
        raise ValidationError(_('Daten Reihenfolge stimmt nicht.'), code='invalid')
