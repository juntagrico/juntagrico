from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.entity.subs import Subscription
from juntagrico.config import Config


class SubscriptionTypeInline(admin.TabularInline):
    model = Subscription.types.through
    verbose_name = _('{0}-Typ').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{0}-Typen').format(Config.vocabulary('subscription'))
    extra = 0
