import itertools
import random
import string

from django.utils import timezone

from juntagrico.config import Config
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.mailer import adminnotification
from juntagrico.mailer import membernotification
from juntagrico.util.temporal import next_membership_end_date


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(
        random.choice(chars) for _ in range(size))


def new_signup(signup_data):
    """ create all elements from data collected during the signup process
    :param signup_data: a CSSessionObject
    :return the main member
    """
    # create member (or get existing)
    member, creation_data = create_or_update_member(signup_data.main_member)

    # create share(s) for member
    create_share(member, signup_data.main_member.new_shares)

    # create subscription for member
    subscription = None
    if sum(signup_data.subscriptions.values()) > 0:
        subscription = create_subscription(signup_data.start_date, signup_data.depot, signup_data.subscriptions, member)

    # add co-members
    for co_member in signup_data.co_members:
        create_or_update_co_member(co_member, subscription, co_member.new_shares)

    # send notifications
    if creation_data['created']:
        membernotification.welcome(member, creation_data['password'])

    return member


def create_or_update_co_member(co_member, subscription, new_shares):
    co_member, creation_data = create_or_update_member(co_member)
    # create share(s) for co-member(s)
    create_share(co_member, new_shares)
    # add co-member to subscription
    add_recipient_to_subscription(subscription, co_member)
    # notify co-member
    membernotification.welcome_co_member(co_member, creation_data['password'], new_shares, new=creation_data['created'])


def create_or_update_member(member):
    created = member.pk is None
    member.save()
    # generate password if member is new
    password = None
    if created:
        password = password_generator()
        member.user.set_password(password)
        member.user.save()
    return member, {
        'created': created,
        'password': password,
    }


def create_share(member, amount=1):
    if amount and Config.enable_shares():
        shares = []
        for i in range(amount):
            shares.append(Share.objects.create(member=member))
        membernotification.shares_created(member, shares)


def create_subscription(start_date, depot, subscription_types, member):
    # create instance
    subscription = Subscription.objects.create(start_date=start_date, depot=depot)
    # add member
    add_recipient_to_subscription(subscription, member)
    subscription.primary_member = member
    subscription.save()
    # set types
    create_subscription_parts(subscription, subscription_types)
    return subscription


def add_recipient_to_subscription(subscription, recipient):
    recipient.join_subscription(subscription)


def create_subscription_parts(subscription, selected_types):
    SubscriptionPart.objects.bulk_create(
        itertools.chain(*[[SubscriptionPart(subscription=subscription, type=sub_type)] * amount
                          for sub_type, amount in selected_types.items()]))


def cancel_sub(subscription, end_date, message):
    if subscription.activation_date is not None and subscription.cancellation_date is None:
        subscription.cancel()
        subscription.end_date = end_date
        subscription.save()
        adminnotification.subscription_canceled(subscription, message)
    elif subscription.activation_date is None and subscription.deactivation_date is None:
        subscription.delete()


def cancel_extra_sub(extra):
    if extra.activation_date is not None:
        extra.cancel()
    elif extra.activation_date is None and extra.deactivation_date is None:
        extra.delete()


def cancel_share(share, now, end_date):
    now = now or timezone.now().date()
    end_date = end_date or next_membership_end_date()
    if share.paid_date is None:
        share.delete()
    else:
        share.cancelled_date = now
        share.termination_date = end_date
        share.save()
