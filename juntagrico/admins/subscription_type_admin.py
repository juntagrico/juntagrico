from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class SubscriptionTypeAdmin(BaseAdmin):

    def get_exclude(self, request, obj=None):
        if not Config.enable_shares():
            return ['shares'] if self.exclude is None else self.exclude.append('shares')
        return self.exclude
