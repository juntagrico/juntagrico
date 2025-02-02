from django.contrib import admin
from django.forms import ModelForm, BooleanField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin, DateRangeExportMixin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.inlines.subscription_membership_inlines import SubscriptionMembershipInline
from juntagrico.config import Config
from juntagrico.resources.member import MemberResource, MemberAssignmentsPerArea, MemberWithAssignmentsAndAreaResource


class MemberAdminForm(ModelForm):
    delete_signup_comment = BooleanField(required=False)

    def clean_delete_signup_comment(self):
        if self.cleaned_data['delete_signup_comment']:
            self.instance.signup_comment = ''
        return None


class MemberAdmin(DateRangeExportMixin, BaseAdmin):
    form = MemberAdminForm
    list_display = ['email', 'first_name', 'last_name', 'number', 'addr_street', 'addr_zipcode', 'addr_location', 'active']
    list_filter = ['user__is_superuser', 'user__is_staff', 'user__groups']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'mobile_phone',
                     'addr_street', 'addr_zipcode', 'addr_location', 'id', 'number']
    readonly_fields = ['signup_comment', 'signup_comment_action', 'user']
    inlines = [SubscriptionMembershipInline]
    fieldsets = [
        (None, {'fields': ['first_name', 'last_name', 'birthday', 'number']}),
        (_('Kontakt'), {'fields': ['email', 'confirmed', 'reachable_by_email', 'phone', 'mobile_phone']}),
        (_('Adresse'), {'fields': ['addr_street', 'addr_zipcode', 'addr_location']}),
        (_('Bankdaten'), {'fields': ['iban']}),
        (_('Status'), {'fields': ['cancellation_date', 'end_date', 'deactivation_date']}),
        (_('Administration'), {'fields': [('signup_comment', 'signup_comment_action'), 'notes', 'user']}),
    ]
    actions = ['impersonate_job']
    resource_classes = [MemberResource, MemberWithAssignmentsAndAreaResource, MemberAssignmentsPerArea]

    @admin.display(
        boolean=True,
        ordering='deactivation_date',
        description=_('Aktiv')
    )
    def active(self, instance):
        return not instance.inactive

    @admin.display(description=_('Löschen?'))
    def signup_comment_action(self, instance):
        disabled = 'disabled="disabled"' if not instance.signup_comment else ''
        return mark_safe(f'<input type="checkbox" name="delete_signup_comment" id="delete_signup_comment" {disabled} />')

    @admin.action(description=Config.vocabulary('member') + ' imitieren (impersonate)...')
    @single_element_action('Genau 1 ' + Config.vocabulary('member') + ' auswählen!')
    def impersonate_job(self, request, queryset):
        inst, = queryset.all()
        return HttpResponseRedirect(reverse('impersonate-start', args=(inst.user.id,)))


class MemberAdminWithShares(MemberAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.readonly_fields.append('share_link')
        self.fieldsets.insert(-1, (Config.vocabulary('share_pl'), {'fields': ['share_link']}))

    @staticmethod
    def _get_multi_link(objs, target):
        return mark_safe('<br>'.join(['<a href="{}">{}</a>'.format(
            reverse(f"admin:{target}", args=(obj.pk,)), obj
        ) for obj in objs]))

    @admin.display(description=Config.vocabulary('share_pl'))
    def share_link(self, obj):
        return self._get_multi_link(obj.share_set.all(), 'juntagrico_share_change') \
            or _('Kein/e/n {}').format(Config.vocabulary('share'))
