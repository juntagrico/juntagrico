from juntagrico.entity.member import Member
from juntagrico.util import addons
from juntagrico_test_addon.admin import MemberShareInline


def show_admin_menu(user):
    return True


addons.config.register_admin_menu('addon_test_admin_menu.html')
addons.config.register_model_inline(Member, MemberShareInline)
addons.config.register_version('testapp', '123')
addons.config.register_show_admin_menu_method(show_admin_menu)
