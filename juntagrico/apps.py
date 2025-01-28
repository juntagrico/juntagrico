from django.apps import AppConfig

from . import checks  # noqa: F401


class JuntagricoAppconfig(AppConfig):
    name = "juntagrico"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
        from .models import Subscription, Share

        signals.depot_changed.connect(signals.on_depot_changed, sender=Subscription)
        signals.share_canceled.connect(signals.on_share_canceled, sender=Share)
        # See models.py for older signal connections
