from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class ExtraSubscriptionTypeAdmin(BaseAdmin):
    exclude = []

    def __init__(self, *args, **kwargs):
        super(ExtraSubscriptionTypeAdmin, self).__init__(*args, **kwargs)
        if not Config.enable_shares():
            self.exclude.append('shares')
