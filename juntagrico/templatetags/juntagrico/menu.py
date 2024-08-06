from django import template
from django.template import loader

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


@register.simple_tag
def widgets_menu(request):
    """
    this allows to store the widgets menu in a variable and reuse it efficiently
    """
    return loader.render_to_string('juntagrico/menu/widgets.html', {}, request)
