from django.apps import AppConfig
from django.contrib.admin import apps

from . import checks  # noqa: F401


class JuntagricoAppconfig(AppConfig):
    name = "juntagrico"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django.db import models
        from . import signals
        from .models import Subscription, Job, Share, Member, SubscriptionMembership
        from .lifecycle.submembership import add_subscription_member_to_activity_area
        from .management.commands import generate_depot_list
        from .management import inject_rename_permissions
        from . import lifecycle, entity

        models.signals.pre_migrate.connect(inject_rename_permissions, sender=self)
        signals.depot_changed.connect(signals.on_depot_changed, sender=Subscription)
        signals.depot_change_confirmed.connect(signals.on_depot_change_confirmed, sender=Subscription)
        signals.canceled.connect(signals.on_member_canceled, sender=Member)
        signals.subscribed.connect(signals.on_job_subscribed, sender=Job)
        signals.assignment_changed.connect(signals.on_assignment_changed, sender=Member)
        signals.share_canceled.connect(signals.on_share_canceled, sender=Share)
        models.signals.post_save.connect(add_subscription_member_to_activity_area, sender=SubscriptionMembership)
        signals.called.connect(signals.on_depot_list_generated, sender=generate_depot_list.Command)
        models.signals.pre_save.connect(lifecycle.membership.pre_save, sender=entity.membership.Membership)

        # See models.py for older signal connections

        '''monkey patch User email method for password reset'''
        from django.contrib.auth.models import User
        User.member__email = property(lambda this: this.member.email)
        User.EMAIL_FIELD = 'member__email'


class JuntagricoAdminConfig(apps.AdminConfig):
    default_site = 'juntagrico.admin_sites.JuntagricoAdminSite'
    default = False
