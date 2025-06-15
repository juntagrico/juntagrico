from django.contrib import admin

from juntagrico.entity.jobs import JobExtra


class JobExtraInline(admin.TabularInline):
    model = JobExtra

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class JobExtraInlineForJobType(JobExtraInline):
    exclude = ['onetime_type']


class JobExtraInlineForOnetimeJob(JobExtraInline):
    exclude = ['recuring_type']
