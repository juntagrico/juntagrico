from django.contrib.admin import register
from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.entity.extrasubs import ExtraSubscription


@register(ExtraSubscription)
class ExtraSubscriptionAdmin(BaseAdmin):
    raw_id_fields = ['main_subscription']
