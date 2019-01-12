from django.contrib import admin

from juntagrico.entity.jobs import JobExtra


class JobExtraInline(admin.TabularInline):
    model = JobExtra

    def get_extra(self, request, obj=None, **kwargs):
        return 0
