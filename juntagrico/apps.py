from django.apps import AppConfig


class JuntagricoAppconfig(AppConfig):
    name = "juntagrico"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
        from .models import Subscription

        signals.depot_changed.connect(signals.on_depot_changed, sender=Subscription)
