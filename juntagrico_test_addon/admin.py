from django.contrib import admin

from juntagrico.entity.share import Share


class MemberShareInline(admin.TabularInline):
    model = Share
    extra = 0
