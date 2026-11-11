from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.entity.subs import SubscriptionAbsence


class SubscriptionAbsenceInline(admin.TabularInline):
    model = SubscriptionAbsence
    verbose_name = _('Absenz')
    verbose_name_plural = _('Absenzen')
    extra = 0
