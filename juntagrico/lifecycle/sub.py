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
    if instance.pk:  # can't access related objects, if sub has not been saved yet.
        if instance.primary_member is not None:
            pm_sub = instance.primary_member in instance.recipients
            pm_form = instance.future_members and instance.primary_member in instance.future_members
            if not (pm_sub or pm_form):
                raise ValidationError(
                    _('HauptbezieherIn muss auch {}-BezieherIn sein').format(Config.vocabulary('subscription')),
                    code='invalid')
        if instance.parts.count() > 0 and instance.future_parts.count() == 0 and instance.cancellation_date is None:
            raise ValidationError(
                _('Nicht gekündigte {0} brauchen mindestens einen aktiven oder wartenden {0}-Bestandteil.'
                  ' Um die Kündigung rückgängig zu machen, leere und speichere zuerst das Kündigungsdatum des Bestandteils und dann jenes vom {0}.').format(
                    Config.vocabulary('subscription')),
                code='invalid')
