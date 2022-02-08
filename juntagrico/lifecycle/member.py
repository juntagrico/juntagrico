from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import adminnotification
from juntagrico.signals import member_deactivated, member_created, member_canceled


def member_post_save(sender, instance, created, **kwargs):
    if created:
        member_created.send(sender=sender, instance=instance)


def member_pre_save(sender, instance, **kwargs):
    check_member_consistency(instance)
    if instance._old['deactivation_date'] != instance.deactivation_date and instance.deactivation_date is not None:
        member_deactivated.send(sender=sender, instance=instance)
    if instance._old['cancellation_date'] != instance.cancellation_date and instance.cancellation_date is not None:
        member_canceled.send(sender=sender, instance=instance)


def handle_member_deactivated(sender, instance, **kwargs):
    instance.areas.clear()


def check_member_consistency(instance):
    if instance._old['deactivation_date'] != instance.deactivation_date and instance.deactivation_date is not None:
        if instance.is_cooperation_member:
            raise ValidationError(
                _('Diese/r/s {} hat mindestens noch ein/e/n aktive/n/s {}').format(Config.vocabulary('member'), Config.vocabulary('share')),
                code='invalid')
        if instance.subscription_future is not None and instance.subscription_future.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch HauptbezieherIn in einer/m {}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')
        if instance.subscription_current is not None and instance.subscription_current.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch HauptbezieherIn in einer/m {}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')


def handle_member_created(sender, instance, **kwargs):
    adminnotification.member_created(instance)
