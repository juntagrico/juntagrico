from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipInline(admin.TabularInline):
    model = SubscriptionMembership
    verbose_name = _('{} Mitgliedschaft').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Mitgliedschaften').format(Config.vocabulary('subscription'))
    extra = 0

