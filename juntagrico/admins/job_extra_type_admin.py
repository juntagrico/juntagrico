from django.contrib import admin

from juntagrico.util.addons import get_jobextratype_inlines


class JobExtraTypeAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_jobextratype_inlines())
        super(JobExtraTypeAdmin, self).__init__(*args, **kwargs)
