from django.contrib import admin


class ListMessageAdmin(admin.ModelAdmin):
    list_display = ['message', 'active']
    search_fields = ['message']
