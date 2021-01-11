from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.lifecycle.submembership import check_submembership_parent_dates
from juntagrico.lifecycle.subpart import check_subpart_parent_dates
from juntagrico.mailer import adminnotification
from juntagrico.signals import sub_activated, sub_deactivated, sub_canceled, sub_created
from juntagrico.util.lifecycle import handle_activated_deactivated, cancel_extra_sub
from juntagrico.util.models import q_activated


def sub_post_save(sender, instance, created, **kwargs):
    if created:
        sub_created.send(sender=sender, instance=instance)


def sub_pre_save(sender, instance, **kwargs):
    with transaction.atomic():
        check_sub_reactivation(instance)
        instance.check_date_order()
        handle_activated_deactivated(instance, sender, sub_activated, sub_deactivated)
        if instance._old['cancellation_date'] is None and instance.cancellation_date is not None:
            sub_canceled.send(sender=sender, instance=instance)
        check_children_dates(instance)
        check_sub_primary(instance)


def handle_sub_activated(sender, instance, **kwargs):
    activation_date = instance.activation_date or timezone.now().date()
    for member in instance.recipients:
        current_sub = member.subscription_current is not None
        sub_deactivated = current_sub and member.subscription_current.deactivation_date is not None
        dates_do_not_overlap = current_sub and sub_deactivated and member.subscription_current.deactivation_date <= activation_date
        if (current_sub and not sub_deactivated) or (current_sub and sub_deactivated and not dates_do_not_overlap):
            raise ValidationError(
                _('Ein Bezüger hat noch ein/e/n aktive/n/s {0}').format(Config.vocabulary('subscription')),
                code='invalid')
    instance.activation_date = activation_date
    change_date = instance.activation_date
    for part in instance.future_parts.all():
        part.activate(change_date)
    for sub_membership in instance.subscriptionmembership_set.all():
        sub_membership.join_date = change_date
        sub_membership.save()


def handle_sub_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date or timezone.now().date()
    change_date = instance.deactivation_date
    for extra in instance.extra_subscription_set.all():
        extra.deactivate(change_date)
    for part in instance.active_parts.all():
        part.deactivate(change_date)
    for part in instance.future_parts.all():
        part.delete()
    for sub_membership in instance.subscriptionmembership_set.all():
        sub_membership.member.leave_subscription(instance, change_date)


def handle_sub_canceled(sender, instance, **kwargs):
    instance.cancellation_date = instance.cancellation_date or timezone.now().date()
    for extra in instance.extra_subscription_set.all():
        cancel_extra_sub(extra)
    for part in instance.parts.filter(q_activated()).all():
        part.cancel()
    for part in instance.parts.filter(~q_activated()).all():
        part.delete()


def handle_sub_created(sender, instance, **kwargs):
    adminnotification.subscription_created(instance)


def check_sub_consistency(instance):
    check_sub_reactivation(instance)
    instance.check_date_order()
    check_children_dates(instance)
    check_sub_primary(instance)


def check_sub_reactivation(instance):
    if instance._old['deactivation_date'] is not None and instance.deactivation_date is None:
        raise ValidationError(
            _('Deaktivierte {0} können nicht wieder aktiviert werden').format(Config.vocabulary('subscription_pl')),
            code='invalid')


def check_sub_primary(instance):
    pm_sub = instance.primary_member in instance.recipients
    pm_form = instance._future_members and instance.primary_member in instance._future_members
    if instance.primary_member is not None and not (pm_sub or pm_form):
        raise ValidationError(
            _('HauptbezieherIn muss auch {}-BezieherIn sein').format(Config.vocabulary('subscription')),
            code='invalid')
    if instance.parts.count() > 0 and instance.future_parts.count() == 0 and instance.cancellation_date is None:
        raise ValidationError(
            _('Nicht gekündigte {0} brauchen mindestens einen aktiven oder wartenden {0}-Bestandteil').format(
                Config.vocabulary('subscription')),
            code='invalid')


def check_children_dates(instance):
    try:
        for part in instance.parts.all():
            check_subpart_parent_dates(part, instance)
        for extra in instance.extra_subscription_set.all():
            check_subpart_parent_dates(extra, instance)
    except ValidationError:
        raise ValidationError(
            _(
                'Aktivierungs- oder Deaktivierungsdatum passt nicht zum untergeordneten Aktivierungs- oder Deaktivierungsdatum'),
            code='invalid')
    try:
        for membership in instance.subscriptionmembership_set.all():
            check_submembership_parent_dates(membership)
    except ValidationError:
        raise ValidationError(
            _('Aktivierungs- oder Deaktivierungsdatum passt nicht zum untergeordneten Beitritts- oder Austrittsdatum'),
            code='invalid')
