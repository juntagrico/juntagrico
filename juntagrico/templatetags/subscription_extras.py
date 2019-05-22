from django import template

register = template.Library()


@register.filter
def future_amount_by_type(subscription, type):
    if not hasattr(subscription, 'future_amount_by_type'):
        return 0
    return subscription.future_amount_by_type(type)