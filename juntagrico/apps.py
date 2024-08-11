from django.apps import AppConfig

from . import checks  # noqa: F401


class JuntagricoAppconfig(AppConfig):
    name = "juntagrico"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
        from .models import Subscription, Job

        signals.depot_changed.connect(signals.on_depot_changed, sender=Subscription)
        signals.subscribed.connect(signals.on_job_subscribed, sender=Job)

        '''monkey patch User email method for password reset'''
        from django.contrib.auth.models import User
        User.member__email = property(lambda this: this.member.email)
        User.EMAIL_FIELD = 'member__email'
