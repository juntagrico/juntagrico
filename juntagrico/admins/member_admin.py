from django.contrib import messages
from django.http import HttpResponseRedirect

from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.member_admin_form import MemberAdminForm
from juntagrico.config import Config


class MemberAdmin(BaseAdmin):
    form = MemberAdminForm
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name', 'email']
    # raw_id_fields = ['subscription']
    exclude = ['future_subscription', 'subscription', 'old_subscriptions']
    readonly_fields = ['user']
    actions = ['impersonate_job']

    def impersonate_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request, 'Genau 1 ' + Config.vocabulary('member') + ' auswählen!', level=messages.ERROR)
            return HttpResponseRedirect('')
        inst, = queryset.all()
        return HttpResponseRedirect('/impersonate/%s/' % inst.user.id)

    impersonate_job.short_description = Config.vocabulary(
        'member') + ' imitieren (impersonate)...'
