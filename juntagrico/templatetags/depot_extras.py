from django import template
from django.db.models import Sum
from django.db.models.query import QuerySet

from juntagrico.entity.subs import Subscription

register = template.Library()


@register.filter
def count(subscriptions):
    if isinstance(subscriptions, QuerySet):
        return subscriptions.count()  # for efficiency
    return len(subscriptions)


@register.filter
def count_units(subscriptions):
    # sum each unit of each subscription type
    units = subscriptions.aggregate(units=Sum('types__size__units'))
    return units['units'] or 0


@register.filter
def sub_size(subscriptions, size):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return [subscriptions] if subscriptions.types.filter(size=size) else []
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(types__size=size)


@register.filter
def extra_sub_type(subscriptions, es_type):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return subscriptions.extra_subscription_set.filter(type=es_type, active=True)
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(extra_subscription_set__type=es_type, extra_subscription_set__active=True)


@register.filter
def weekday(queryset_or_sub, weekday_id):
    # case 1: single subscription object is passed
    if isinstance(queryset_or_sub, Subscription):
        return [queryset_or_sub] if queryset_or_sub.depot.weekday == weekday_id else []
    # case 2: queryset of subscriptions or depots is passed
    if queryset_or_sub.model == Subscription:
        return queryset_or_sub.filter(depot__weekday=weekday_id)
    return queryset_or_sub.filter(weekday=weekday_id)


@register.filter
def depot(subscriptions, depot):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return [subscriptions] if subscriptions.depot == depot else []
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(depot=depot)
