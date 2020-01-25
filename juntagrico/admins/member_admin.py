from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.member_admin_form import MemberAdminForm
from juntagrico.config import Config


class MemberAdmin(BaseAdmin):
    form = MemberAdminForm
    list_display = ['email', 'first_name', 'last_name', 'active']
    search_fields = ['first_name', 'last_name', 'email']
    exclude = ['future_subscription', 'subscription', 'old_subscriptions']
    readonly_fields = ['user']
    actions = ['impersonate_job']

    def active(self, instance):
        return not instance.inactive

    active.short_description = _('Aktiv')
    active.boolean = True

    def impersonate_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request, 'Genau 1 ' + Config.vocabulary('member') + ' auswählen!', level=messages.ERROR)
            return HttpResponseRedirect('')
        inst, = queryset.all()
        return HttpResponseRedirect('/impersonate/%s/' % inst.user.id)

    impersonate_job.short_description = Config.vocabulary(
        'member') + ' imitieren (impersonate)...'
