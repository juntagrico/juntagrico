from juntagrico.entity.member import Member
from juntagrico.util import addons
from juntagrico_test_addon.admin import MemberShareInline


addons.config.register_admin_menu('addon_test_admin_menu.html')
addons.config.register_model_inline(Member, MemberShareInline)
