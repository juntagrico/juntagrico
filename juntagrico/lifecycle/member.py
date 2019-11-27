from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import AdminNotification
from juntagrico.signals import member_deactivated, member_created, member_canceled


def member_post_save(sender, instance, created, **kwargs):
    if created:
        member_created.send(sender=sender, instance=instance)


def member_pre_save(sender, instance, **kwargs):
    check_member_consistency(instance)
    if instance._old['inactive'] != instance.inactive and instance.inactive is True:
        member_deactivated.send(sender=sender, instance=instance)
    if instance._old['canceled'] != instance.canceled and instance.canceled is True:
        member_canceled.send(sender=sender, instance=instance)


def handle_member_deactivated(sender, instance, **kwargs):
    instance.areas.clear()


def check_member_consistency(instance):
    if instance._old['inactive'] != instance.inactive and instance.inactive is True:
        if instance.share_set.filter(payback_date__isnull=True).count() > 0:
            raise ValidationError(
                _('Diese/r/s {} hat mindestens noch ein/e/n aktive/n/s {}').format(Config.vocabulary('member'), Config.vocabulary('share')),
                code='invalid')
        if instance.future_subscription is not None and instance.future_subscription.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch HauptbezieherIn in einer/m {}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')
        if instance.subscription is not None and instance.subscription.primary_member.pk == instance.pk:
            raise ValidationError(
                _('Diese/r/s {} ist noch HauptbezieherIn in einer/m {}').format(Config.vocabulary('member'), Config.vocabulary('subscription')),
                code='invalid')


def handle_member_created(sender, instance, **kwargs):
    AdminNotification.member_created(instance)
