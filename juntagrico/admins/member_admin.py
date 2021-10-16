from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.subs import Subscription


class MemberAdmin(BaseAdmin):
    list_display = ['email', 'first_name', 'last_name', 'active']
    list_filter = ['user__is_superuser', 'user__is_staff', 'user__groups']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'mobile_phone']
    exclude = ['future_subscription', 'subscription', 'old_subscriptions']
    readonly_fields = ['subscription_link', 'future_subscription_link', 'old_subscription_link', 'user']
    fieldsets = [
        (None, {'fields': ['first_name', 'last_name', 'birthday']}),
        (_('Kontakt'), {'fields': ['email', 'confirmed', 'reachable_by_email', 'phone', 'mobile_phone']}),
        (_('Adresse'), {'fields': ['addr_street', 'addr_zipcode', 'addr_location']}),
        (_('Bankdaten'), {'fields': ['iban']}),
        (_('Status'), {'fields': ['cancellation_date', 'end_date', 'deactivation_date']}),
        (Config.vocabulary('subscription_pl'),
         {'fields': ['subscription_link', 'future_subscription_link', 'old_subscription_link']}),
        (_('Administration'), {'fields': ['notes', 'user']}),
    ]
    actions = ['impersonate_job']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        request.GET = request.GET.copy()
        name = request.GET.pop('qs_name', ['all'])[0]
        subscription_id = request.GET.pop('sub_id', ['0'])[0]
        if name == 'cs':
            return MemberDao.members_for_create_subscription()
        elif name == 'fs':
            subscription = Subscription.objects.get(id=int(subscription_id))
            return MemberDao.members_for_future_subscription(subscription)
        elif name == 's':
            subscription = Subscription.objects.get(id=int(subscription_id))
            return MemberDao.members_for_subscription(subscription)
        return queryset

    @admin.display(
        boolean=True,
        ordering='deactivation_date',
        description=_('Aktiv')
    )
    def active(self, instance):
        return not instance.inactive

    @admin.action(description=Config.vocabulary('member') + ' imitieren (impersonate)...')
    @single_element_action('Genau 1 ' + Config.vocabulary('member') + ' auswählen!')
    def impersonate_job(self, request, queryset):
        inst, = queryset.all()
        return HttpResponseRedirect('/impersonate/%s/' % inst.user.id)

    @admin.display(description=Config.vocabulary('subscription'))
    def subscription_link(self, obj):
        return self._get_single_link(obj.subscription_current, 'juntagrico_subscription_change') \
            or _('Kein/e {}').format(Config.vocabulary('subscription'))

    @admin.display(description=_('Zukünftige/r/s {}').format(Config.vocabulary('subscription')))
    def future_subscription_link(self, obj):
        return self._get_single_link(obj.subscription_future, 'juntagrico_subscription_change') \
            or _('Kein/e zukünftige/r/s {}').format(Config.vocabulary('subscription'))

    @admin.display(description=_('Alte {}').format(Config.vocabulary('subscription_pl')))
    def old_subscription_link(self, obj):
        return self._get_multi_link(obj.subscriptions_old.all(), 'juntagrico_subscription_change') \
            or _('Keine alten {}').format(Config.vocabulary('subscription_pl'))

    @staticmethod
    def _get_single_link(obj, target):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse(f"admin:{target}", args=(obj.pk,)), obj
        )) if obj else ''

    @staticmethod
    def _get_multi_link(objs, target):
        return mark_safe('<br>'.join(['<a href="{}">{}</a>'.format(
            reverse(f"admin:{target}", args=(obj.pk,)), obj
        ) for obj in objs]))


class MemberAdminWithShares(MemberAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.readonly_fields.append('share_link')
        self.fieldsets.insert(-1, (Config.vocabulary('share_pl'), {'fields': ['share_link']}))

    @admin.display(description=Config.vocabulary('share_pl'))
    def share_link(self, obj):
        return self._get_multi_link(obj.share_set.all(), 'juntagrico_share_change') \
            or _('Kein/e/n {}').format(Config.vocabulary('share'))
