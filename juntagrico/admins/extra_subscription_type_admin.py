from django.contrib.admin import register
from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.config import Config
from juntagrico.entity.extrasubs import ExtraSubscriptionType


@register(ExtraSubscriptionType)
class ExtraSubscriptionTypeAdmin(BaseAdmin):
    exclude = []


if not Config.enable_shares():
    ExtraSubscriptionTypeAdmin.exclude.append('shares')
