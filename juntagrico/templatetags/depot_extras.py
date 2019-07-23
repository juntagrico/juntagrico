from django import template

register = template.Library()


@register.filter
def subscriptions_amount(subscription, id):
    return subscription.subscription_amount(id)


@register.filter
def extra_subscription(subscription, code):
    return subscription.extra_subscription(code)


@register.filter
def extra_subscription_amount(subscription, code):
    return subscription.extra_subscription_amount(code)
