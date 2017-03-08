from django import template

register = template.Library()


@register.filter
def subscriptions_amount(subscription, name):
    return subscription.subscription_amount(name)
    
@register.filter
def extra_subscription(subscription, code):
    return subscription.extra_subscription(code)
    
