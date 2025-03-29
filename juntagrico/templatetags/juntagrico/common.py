from django import template
from django.conf import settings
from django.template.defaultfilters import urlize, linebreaksbr

from juntagrico import __version__
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.deliverydao import DeliveryDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.jobextradao import JobExtraDao
from juntagrico.entity.subtypes import SubscriptionType

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if not hasattr(dictionary, 'get'):
        return False
    return dictionary.get(key)


@register.simple_tag
def has_extra_subscriptions():
    return SubscriptionType.objects.is_extra().exists()


@register.simple_tag
def show_core():
    return ActivityAreaDao.all_core_areas().count() > 0


@register.simple_tag
def requires_core():
    return SubscriptionType.objects.filter(required_core_assignments__gt=0).exists()


@register.simple_tag
def show_job_extras():
    return JobExtraDao.all_job_extras().count() > 0


@register.simple_tag
def show_deliveries(request):
    return DeliveryDao.deliveries_by_subscription(request.user.member.subscription_current).exists()


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
        return DepotDao.depots_for_contact(request.user.member)
    return []


@register.simple_tag
def area_admin(request):
    if hasattr(request.user, 'member'):
        return ActivityAreaDao.areas_by_coordinator(request.user.member)
    return []


@register.simple_tag
def get_version():
    return __version__


@register.filter
def richtext(value):
    if 'djrichtextfield' not in settings.INSTALLED_APPS or not hasattr(settings, 'DJRICHTEXTFIELD_CONFIG'):
        value = urlize(value)
        value = linebreaksbr(value)
    return value


@register.filter
def values_list(queryset, keys):
    return queryset.values_list(keys, flat=isinstance(keys, str))
