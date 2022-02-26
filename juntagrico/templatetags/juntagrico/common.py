from django import template
from django.conf import settings
from django.template.defaultfilters import urlize, linebreaksbr

from juntagrico import version
from juntagrico.dao.deliverydao import DeliveryDao
from juntagrico.dao.jobextradao import JobExtraDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.subtypes import SubscriptionType, SubscriptionProduct

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if not hasattr(dictionary, 'get'):
        return False
    return dictionary.get(key)


@register.simple_tag
def has_extra_subscriptions():
    return SubscriptionProduct.extras.count() > 0


@register.simple_tag
def show_core():
    return ActivityArea.objects.core().count() > 0


@register.simple_tag
def requires_core():
    return SubscriptionType.objects.filter(required_core_assignments__gt=0).count() > 0


@register.simple_tag
def show_job_extras():
    return JobExtraDao.all_job_extras().count() > 0


@register.simple_tag
def show_deliveries(request):
    return len(DeliveryDao.deliveries_by_subscription(request.user.member.subscription_current)) > 0


@register.filter
def activemenu(request, expected):
    actual = getattr(request, 'active_menu', '')
    if actual == expected:
        return 'active'
    return ''


@register.simple_tag
def messages(request):
    return getattr(request, 'member_messages', [])


@register.filter
def view_name(request):
    return request.resolver_match.view_name.replace('.', '-')


@register.simple_tag
def depot_admin(request):
    if hasattr(request.user, 'member'):
        return request.user.member.depot_set
    return Depot.objects.none()


@register.simple_tag
def area_admin(request):
    if hasattr(request.user, 'member'):
        return request.user.member.coordinating_areas.all()
    return ActivityArea.objects.none()


@register.simple_tag
def get_version():
    return version


@register.filter
def richtext(value):
    if 'djrichtextfield' not in settings.INSTALLED_APPS or not hasattr(settings, 'DJRICHTEXTFIELD_CONFIG'):
        value = urlize(value)
        value = linebreaksbr(value)
    return value
