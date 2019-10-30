from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class ExtraSubscriptionTypeAdmin(BaseAdmin):
    exclude = []

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        if not Config.enable_shares():
            self.exclude.append('shares')
