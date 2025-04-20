from django.contrib import admin

from juntagrico.entity.share import Share
from juntagrico.entity.member import Member
from juntagrico.util import addons


class MemberShareInline(admin.TabularInline):
    model = Share
    extra = 0


addons.config.register_model_inline(Member, MemberShareInline)
