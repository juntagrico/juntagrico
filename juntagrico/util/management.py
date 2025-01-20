import itertools

from juntagrico.config import Config
from juntagrico.entity.share import Share
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.mailer import adminnotification
from juntagrico.mailer import membernotification
from juntagrico.util.users import make_password


def create_or_update_co_member(co_member, subscription, new_shares):
    co_member, creation_data = create_or_update_member(co_member)
    # create share(s) for co-member(s)
    create_share(co_member, new_shares)
    # add co-member to subscription
    co_member.join_subscription(subscription)
    # notify co-member
    membernotification.welcome_co_member(co_member, creation_data['password'], new_shares, new=creation_data['created'])


def create_or_update_member(member):
    created = member.pk is None
    member.save()
    # generate password if member is new
    password = None
    if created:
        password = make_password()
        member.user.set_password(password)
        member.user.save()
    return member, {
        'created': created,
        'password': password,
    }


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
