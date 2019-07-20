from juntagrico.config import Config
from juntagrico.signals import share_created
from juntagrico.util.bills import bill_share


def share_post_save(sender, instance, created, **kwargs):
    share_created.send(sender=sender, instance=instance, created=created)


def handle_share_created(sender, instance, created, **kwargs):
    if created and Config.billing():
        bill_share(instance)
