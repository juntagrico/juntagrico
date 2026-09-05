from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.entity.subs import SubscriptionSurcharge


class SubscriptionSurchargeInline(admin.TabularInline):
    model = SubscriptionSurcharge
    verbose_name = _('Aufschlag/Abschlag')
    verbose_name_plural = _('Aufschläge/Abschläge')
    extra = 0
