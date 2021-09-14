from django import template

from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.util import addons

register = template.Library()


@register.simple_tag
def show_admin_menu(request):
    user = request.user
    if not user.is_authenticated:
        return False
    perms = ['juntagrico.change_subscription',
             'juntagrico.change_subscriptionpart',
             'juntagrico.change_member',
             'juntagrico.change_assignment',
             'juntagrico.change_share',
             'juntagrico.can_filter_subscriptions',
             'juntagrico.can_filter_members',
             'juntagrico.can_send_mails',
             'juntagrico.can_view_lists',
             'juntagrico.can_view_exports',
             'can_view_exports']
    has_perm = set(user.get_all_permissions()) & set(perms)
    is_area_admin = ActivityAreaDao.areas_by_coordinator(user.member).count() > 0
    is_depot_admin = DepotDao.depots_for_contact(user.member).count() > 0
    return user.is_staff or has_perm or is_area_admin or is_depot_admin or addons.config.show_admin_menu(user)


@register.simple_tag
def admin_menus():
    return addons.config.get_admin_menus()


@register.simple_tag
def admin_subscription_menus():
    return addons.config.get_admin_subscription_menu()


@register.simple_tag
def user_menus():
    return addons.config.get_user_menus()
