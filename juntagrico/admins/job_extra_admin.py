from django.contrib import admin

from juntagrico.util.addons import get_jobextra_inlines


class JobExtraAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_jobextra_inlines())
        super(JobExtraAdmin, self).__init__(*args, **kwargs)
