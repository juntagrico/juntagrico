from django import template
from django.db.models import Sum, Model
from django.db.models.query import QuerySet

from juntagrico.entity.subs import Subscription, SubscriptionPart
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
def count_units(subs_or_types, date=None):
    if not subs_or_types:
        return 0
    if isinstance(subs_or_types, Subscription):
        # case 1: single subscription object is passed
        units = subs_or_types.parts.on_depot_list().active_on(date).aggregate(units=Sum('type__size__units'))
    elif isinstance(subs_or_types, QuerySet):
        if subs_or_types.model is Subscription:
            # case 2: sum each unit of each subscription type
            units = {'units': str(sum([float(sub.parts.on_depot_list().active_on(date).aggregate(units=Sum('type__size__units'))['units'] or 0) for sub in subs_or_types.all()]))}
        elif subs_or_types.model is SubscriptionType:
            # case 3: queryset of types is passed
            units = subs_or_types.on_depot_list().aggregate(units=Sum('size__units'))
    return float(units['units'] or 0)


@register.filter
def parts_by_size(subscriptions, size):
    if isinstance(subscriptions, Subscription):
        # case 1: single subscription object is passed
        parts = subscriptions.parts
    else:
        # case 2: queryset of subscriptions is passed
        parts = SubscriptionPart.objects.filter(subscription__in=subscriptions)
    return parts.filter(type__size=size)


@register.filter
def by_tour(subscriptions, tour):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return subscriptions if subscriptions.depot.tour == tour else None
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(depot__tour=tour)


@register.filter
def by_depot(subscriptions, depot):
    # case 1: single subscription object is passed
    if isinstance(subscriptions, Subscription):
        return subscriptions if subscriptions.depot == depot else None
    # case 2: queryset of subscriptions is passed
    return subscriptions.filter(depot=depot)


@register.filter
def active_on(parts, date=None):
    return parts.active_on(date)
