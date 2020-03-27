from django import template
from django.db.models import Sum, Model
from django.db.models.query import QuerySet

from juntagrico.entity.extrasubs import ExtraSubscription
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionType

register = template.Library()


@register.filter
def count(entity):
    if not entity:
        return 0
    if isinstance(entity, Model):
        return 1
    if isinstance(entity, QuerySet):
        return entity.count()  # for efficiency
    return len(entity)


@register.filter
def count_units(subs_or_types):
    if not subs_or_types:
        return 0
    if isinstance(subs_or_types, Subscription):
        # case 1: single subscription object is passed
        units = subs_or_types.types.aggregate(units=Sum('size__units'))
    elif isinstance(subs_or_types, QuerySet):
        if subs_or_types.model is Subscription:
            # case 2: sum each unit of each subscription type
            units = subs_or_types.aggregate(units=Sum('types__size__units'))
        elif subs_or_types.model is SubscriptionType:
            # case 3: queryset of types is passed
            units = subs_or_types.aggregate(units=Sum('size__units'))
    return int(units['units'] or 0)


@register.filter
def get_types_by_size(subscriptions, size):
    if isinstance(subscriptions, Subscription):
        # case 1: single subscription object is passed
        types = subscriptions.types
    else:
        # case 2: queryset of subscriptions is passed
        types = SubscriptionType.objects.filter(subscription_set__in=subscriptions)
    return types.filter(size=size)


@register.filter
def get_extra_subs_by_type(subscriptions, es_type):
    if isinstance(subscriptions, Subscription):
        # case 1: single subscription object is passed
        es = subscriptions.extra_subscription_set
    else:
        # case 2: queryset of subscriptions is passed
        es = ExtraSubscription.objects.filter(main_subscription__in=subscriptions)
    return es.filter(type=es_type, active=True)


@register.filter
def by_weekday(queryset_or_sub, weekday_id):
    # case 1: single subscription object is passed
    if isinstance(queryset_or_sub, Subscription):
        return queryset_or_sub if queryset_or_sub.depot.weekday == weekday_id else None
    # case 2: queryset of subscriptions or depots is passed
    if queryset_or_sub.model == Subscription:
        return queryset_or_sub.filter(depot__weekday=weekday_id)
    return queryset_or_sub.filter(weekday=weekday_id)


@register.filter
def by_depot(subscriptions, depot):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return subscriptions if subscriptions.depot == depot else None
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(depot=depot)
