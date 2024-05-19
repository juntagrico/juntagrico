from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from juntagrico.config import Config


def sub_pre_save(sender, instance, **kwargs):
    with transaction.atomic():
        check_sub_primary(instance)


def check_sub_consistency(instance):
    check_sub_primary(instance)


def check_sub_primary(instance):
    if instance.primary_member is not None:
        # compatibility fix. See https://github.com/juntagrico/juntagrico/pull/641
        pm_sub = instance.pk and instance.primary_member in instance.recipients
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
