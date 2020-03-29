from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class ExtraSubscriptionTypeAdmin(BaseAdmin):
    exclude = []


if not Config.enable_shares():
    ExtraSubscriptionTypeAdmin.exclude.append('shares')
