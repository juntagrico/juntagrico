import datetime

from django import template
from impersonate.helpers import check_allow_for_user

register = template.Library()


@register.inclusion_tag('snippets/impersonation_link.html')
def impersonate_start(request, member):
    user = member.user
    return {
        'can_impersonate': check_allow_for_user(request, user),
        'user': user
    }


@register.inclusion_tag('juntagrico/snippets/depot/fee.html')
def depot_fee(depot, subscription_count, prefix='', postfix=''):
    return {
        'fee': depot.total_fee(subscription_count),
        'prefix': prefix,
        'postfix': postfix
    }


@register.simple_tag
def subscription_depot_fee(subscription_type, depot=''):
    fee = 0
    if depot != '':
        condition = subscription_type.depot_conditions.filter(depot=depot).first()
        fee = condition.fee if condition else 0
    return fee


@register.inclusion_tag('juntagrico/snippets/action_date.html')
def action_date(request):
    change_date = request.session.get('changedate', None)
    date_changed = change_date is not None
    change_date = change_date or datetime.date.today()
    return {'change_date': change_date, 'date_changed': date_changed}
