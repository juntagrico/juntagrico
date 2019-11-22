from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.signals import sub_activated, sub_deactivated, sub_canceled
from juntagrico.util.bills import bill_subscription
from juntagrico.util.lifecycle import handle_activated_deactivated


def sub_pre_save(sender, instance, **kwargs):
    check_sub_consistency(instance)
    handle_activated_deactivated(instance, sender, sub_activated, sub_deactivated)
    if instance._old['canceled'] != instance.canceled:
        sub_canceled.send(sender=sender, instance=instance)


def handle_sub_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date if instance.activation_date is not None else timezone.now().date()
    for member in instance.recipients_all_for_state('waiting'):
        if member.subscription is not None:
            raise ValidationError(
                _('Ein Bezüger hat noch ein/e/n aktive/n/s {0}').format(Config.vocabulary('subscription')),
                code='invalid')
    for member in instance.recipients_all_for_state('waiting'):
        member.subscription = instance
        member.future_subscription = None
        member.save()
    if Config.billing():
        bill_subscription(instance)


def handle_sub_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date if instance.deactivation_date is not None else timezone.now().date()
    for member in instance.recipients_all_for_state('active'):
        member.old_subscriptions.add(instance)
        member.subscription = None
        if member.active_shares_count == 0:
            member.inactive = True
        member.save()


def handle_sub_canceled(sender, instance, **kwargs):
    instance.cancelation_date = timezone.now().date()


def check_sub_consistency(instance):
    if instance._old['active'] != instance.active and instance._old['deactivation_date'] is not None:
        raise ValidationError(
            _('Deaktivierte {0} koennen nicht wieder aktiviert werden').format(Config.vocabulary('subscription_pl')),
            code='invalid')
