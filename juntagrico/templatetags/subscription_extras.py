from django import template

register = template.Library()


@register.filter
def future_amount_by_type(subscription, type):
    return subscription.future_amount_by_type(type)