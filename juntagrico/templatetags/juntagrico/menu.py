from django import template

from juntagrico.util import addons

register = template.Library()


@register.simple_tag
def admin_menus():
    return addons.config.get_admin_menus()


@register.simple_tag
def admin_subscription_menus():
    return addons.config.get_admin_subscription_menu()


@register.simple_tag
def user_menus():
    return addons.config.get_user_menus()
