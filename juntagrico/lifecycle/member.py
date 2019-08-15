from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.signals import member_deactivated


def member_pre_save(sender, instance, **kwargs):
    if instance._old['inactive'] != instance.inactive and instance._old['inactive'] is False:
        member_deactivated.send(sender=sender, instance=instance)
    check_member_consistency(instance)


def handle_member_deactivated(sender, instance, **kwargs):
    instance.areas.clear()


def check_member_consistency(instance):
    if instance._old['inactive'] != instance.inactive and instance._old['inactive'] is False:
        if instance.share_set.filter(payback_date__isnull=True).count() > 0:
            raise ValidationError(
                _('Diese/r/s {} hat mindestens noch ein/e/n aktive/n/s {0}').format(Config.vocabulary('member'), Config.vocabulary('share')),
                code='invalid')
        if instance.future_subscription is not None and instance.future_subscription.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch Hauptabonnent in einer/m {0}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')
        if instance.subscription is not None and instance.subscription.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch Hauptabonnent in einer/m {0}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')
