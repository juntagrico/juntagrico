from django import template
from django.db.models import Model
from django.db.models.query import QuerySet

from juntagrico.entity.subs import Subscription, SubscriptionPart

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
def count_units(subs, date=None):
    if not subs:
        return 0.0
    units = 0.0
    if isinstance(subs, Subscription):
        # case 1: single subscription object is passed
        units = float(subs.parts.on_depot_list().active_on(date).count_units())
    elif isinstance(subs, QuerySet):
        if subs.model is Subscription:
            # case 2: sum each unit of each subscription type
            units = sum(
                float(
                    sub.parts.on_depot_list().active_on(date).count_units() or 0
                ) for sub in subs.all()
            )
    return units


@register.filter
def parts_by_size(subscriptions, product_size):
    if isinstance(subscriptions, Subscription):
        # case 1: single subscription object is passed
        parts = subscriptions.parts
    else:
        # case 2: queryset of subscriptions is passed
        parts = SubscriptionPart.objects.filter(subscription__in=subscriptions)
    return parts.filter(type__bundle__product_sizes=product_size)


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
