import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.lifecycle import parse_date


def pre_save(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        check_membership_consistency(instance)


def check_membership_consistency(instance):
    instance.check_date_order()
    if hasattr(instance, 'account'):
        memberships = instance.account.memberships.exclude(pk=instance.pk)
        activation_date = instance.activation_date
        deactivation_date = parse_date(instance.deactivation_date)
        today = datetime.date.today()
        if activation_date is None:
            # can only request membership if no other membership is active
            check = Q(deactivation_date__isnull=True) | Q(deactivation_date__gte=today)
        elif deactivation_date is None:
            # can only have active membership if no other membership is active at the same time
            check = Q(activation_date__isnull=False, deactivation_date__isnull=True) | Q(deactivation_date__gte=activation_date)
        else:
            check = Q(activation_date__lte=deactivation_date, deactivation_date__isnull=True) | \
                    Q(activation_date__lte=deactivation_date, deactivation_date__gte=deactivation_date) | \
                    Q(activation_date__lte=activation_date, deactivation_date__gte=activation_date)
            if deactivation_date >= today:
                check |= Q(activation_date__isnull=True)
        if memberships.filter(check).exists():
            raise ValidationError(
                _('{} kann nur 1 {} gleichzeitig aktiv oder beantragt haben.').format(
                    Config.vocabulary('member'),
                    Config.vocabulary('membership')
                ),
                code='overlap'
            )
