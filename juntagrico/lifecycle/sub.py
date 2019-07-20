from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.signals import sub_activated, sub_deactivated, sub_canceled
from juntagrico.util.bills import bill_subscription


def sub_pre_save(sender, instance, **kwargs):
    if instance._old['active'] != instance.active and instance._old['active'] is False and instance.deactivation_date is None:
        sub_activated.send(sender=sender, instance=instance)
    elif instance._old['active'] != instance.active and instance._old['active'] is True and instance.deactivation_date is None:
        sub_deactivated.send(sender=sender, instance=instance)
    if instance._old['canceled'] != instance.canceled:
        sub_canceled.send(sender=sender, instance=instance)


def handle_sub_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date if instance.activation_date is not None else timezone.now().date()
    for member in instance.recipients_all_for_state('waiting'):
        if member.subscription is not None:
            raise ValidationError(
                _('Ein Bezüger hat noch ein/e/n aktive/n/s {0}').format(Config.vocabulary('subscription_')),
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
        member.save()


def handle_sub_canceled(sender, instance, **kwargs):
    instance.cancelation_date = timezone.now().date()
