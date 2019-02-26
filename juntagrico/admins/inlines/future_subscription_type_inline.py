from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.entity.subs import Subscription
from juntagrico.config import Config


class FutureSubscriptionTypeInline(admin.TabularInline):
    model = Subscription.future_types.through
    verbose_name = _('Zukunft {0}-Typ').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('Zukunft {0}-Typen').format(Config.vocabulary('subscription'))
    extra = 0