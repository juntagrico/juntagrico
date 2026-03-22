import itertools

from juntagrico.config import Config
from juntagrico.entity.share import Share
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.mailer import adminnotification
from juntagrico.mailer import membernotification


def create_share(member, amount=1):
    if amount and Config.enable_shares():
        shares = []
        for _ in range(amount):
            shares.append(Share.objects.create(member=member))
        membernotification.shares_created(member, shares)


def create_subscription_parts(subscription, selected_types, notify=False):
    """
    :param subscription: subscription to add the parts to
    :param selected_types: a dict of subscription_types -> amount
    :param notify: if True will send an admin notification
    """
    parts = SubscriptionPart.objects.bulk_create(
        itertools.chain(*[[SubscriptionPart(subscription=subscription, type=sub_type)] * amount
                          for sub_type, amount in selected_types.items()]))
    if notify:
        adminnotification.subparts_created(parts, subscription)


def cancel_sub(subscription, end_date, message):
    subscription.cancel()
    subscription.end_date = end_date
    subscription.save()
    adminnotification.subscription_canceled(subscription, message)
