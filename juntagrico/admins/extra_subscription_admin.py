from juntagrico.admins import BaseAdmin


class ExtraSubscriptionAdmin(BaseAdmin):
    raw_id_fields = ['main_subscription']
