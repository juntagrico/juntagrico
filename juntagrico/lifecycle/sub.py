import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.lifecycle.submembership import check_submembership_parent_dates
from juntagrico.lifecycle.subpart import check_subpart_parent_dates
from juntagrico.signals import sub_activated, sub_deactivated, sub_canceled, sub_created
from juntagrico.util.lifecycle import handle_activated_deactivated


def sub_post_save(sender, instance, created, **kwargs):
    if created:
        sub_created.send(sender=sender, instance=instance)


def sub_pre_save(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        with transaction.atomic():
            check_sub_reactivation(instance)
            instance.check_date_order()
            handle_activated_deactivated(instance, sender, sub_activated, sub_deactivated)
            if instance._old['cancellation_date'] is None and instance.cancellation_date is not None:
                sub_canceled.send(sender=sender, instance=instance)
            check_children_dates(instance)
            check_sub_primary(instance)


def handle_sub_activated(sender, instance, **kwargs):
    if not instance.pk:
        # if sub has not been saved yet django 4.1 throws an error.
        # in django <= 4.0 the activation of parts failed silently
        # reproducing this behaviour here.
        # see https://github.com/juntagrico/juntagrico/pull/641
        return
    activation_date = instance.activation_date or datetime.date.today()
    for member in instance.current_members:
        current_sub = member.subscription_current is not None
        sub_deactivated = current_sub and member.subscription_current.deactivation_date is not None
        dates_do_not_overlap = current_sub and sub_deactivated and member.subscription_current.deactivation_date <= activation_date
        if (current_sub and not sub_deactivated) or (current_sub and sub_deactivated and not dates_do_not_overlap):
            raise ValidationError(
                _('Ein Bezüger hat noch ein/e/n aktive/n/s {0}').format(Config.vocabulary('subscription')),
                code='invalid')
    instance.activation_date = activation_date
    change_date = instance.activation_date
    if not getattr(instance, '__skip_part_activation__', False):
        for part in instance.future_parts.all():
            part.activate(change_date)
    for sub_membership in instance.subscriptionmembership_set.all():
        sub_membership.join_date = change_date
        sub_membership.save()


def handle_sub_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date or datetime.date.today()
    change_date = instance.deactivation_date
    if instance.pk:
        for part in instance.parts.all():
            part.deactivate(change_date)
        for sub_membership in instance.subscriptionmembership_set.all():
            sub_membership.member.leave_subscription(instance, change_date)


def handle_sub_canceled(sender, instance, **kwargs):
    instance.cancellation_date = instance.cancellation_date or datetime.date.today()
    if instance.pk:
        for part in instance.parts.all():
            part.cancel()


def handle_sub_created(sender, instance, **kwargs):
    pass


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
    if instance.primary_member is not None:
        # compatibility fix. See https://github.com/juntagrico/juntagrico/pull/641
        pm_sub = instance.pk and instance.primary_member in instance.current_members
        # this check works also for new instances, because future_members is populated with form data, if available
        pm_form = instance.future_members and instance.primary_member in instance.future_members
        if not (pm_sub or pm_form):
            raise ValidationError(
                _('HauptbezieherIn muss auch {}-BezieherIn sein').format(Config.vocabulary('subscription')),
                code='invalid')
    if instance.pk:  # compatibility fix. See https://github.com/juntagrico/juntagrico/pull/641
        if instance.parts.count() > 0 and instance.future_parts.count() == 0 and instance.cancellation_date is None:
            raise ValidationError(
                _('Nicht gekündigte {0} brauchen mindestens einen aktiven oder wartenden {0}-Bestandteil.'
                  ' Um die Kündigung rückgängig zu machen, leere und speichere zuerst das Kündigungsdatum des Bestandteils und dann jenes vom {0}.').format(
                    Config.vocabulary('subscription')),
                code='invalid')


def check_children_dates(instance):
    if not instance.pk:
        # compatibility fix. See https://github.com/juntagrico/juntagrico/pull/641
        return
    reactivation_info = _(' Um die Aktivierung rückgängig zu machen oder in die Zukunft zu legen, ändere (bzw. leere) und speichere die Daten in dieser Reihenfolge:'
                          ' 1. Aktivierungsdaten der Bestandteile & Beitrittsdaten,'
                          ' 2. Aktivierungsdatum vom {0}').format(Config.vocabulary('subscription'))
    try:
        for part in instance.parts.all():
            # empty end dates are made consistent on save, no need to check
            check_subpart_parent_dates(part, instance, check_empty_end=False)
    except ValidationError as e:
        raise ValidationError(
            _(
                'Aktivierungs- oder Deaktivierungsdatum passt nicht zum untergeordneten Aktivierungs- oder Deaktivierungsdatum.' + reactivation_info),
            code='invalid') from e
    try:
        for membership in instance.subscriptionmembership_set.all():
            # empty end dates are made consistent on save, no need to check
            check_submembership_parent_dates(membership, check_empty_end=False)
    except ValidationError as e:
        raise ValidationError(
            _('Aktivierungs- oder Deaktivierungsdatum passt nicht zum untergeordneten Beitritts- oder Austrittsdatum.' + reactivation_info),
            code='invalid') from e
