import itertools
import random
import string

from juntagrico.config import Config
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import TFSST, TSST
from juntagrico.mailer import MemberNotification, AdminNotification


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(
        random.choice(chars) for _ in range(size))


def new_signup(signup_data):
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
        MemberNotification.welcome(member, creation_data['password'])


def create_or_update_co_member(co_member, subscription, new_shares):
    co_member, creation_data = create_or_update_member(co_member)
    # create share(s) for co-member(s)
    create_share(co_member, new_shares)
    # add co-member to subscription
    add_recipient_to_subscription(subscription, co_member)
    # notify co-member
    MemberNotification.welcome_co_member(co_member, creation_data['password'], new_shares, new=creation_data['created'])


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
        MemberNotification.shares_created(member, shares)


def create_subscription(start_date, depot, subscription_types, member):
    # create instance
    subscription = Subscription.objects.create(start_date=start_date, depot=depot)
    # add member
    add_recipient_to_subscription(subscription, member)
    subscription.primary_member = member
    subscription.save()
    # set types
    replace_subscription_types(subscription, subscription_types)
    return subscription


def add_recipient_to_subscription(subscription, recipient):
    if subscription.state == 'waiting':
        recipients = subscription.members_future
    elif subscription.state == 'inactive':
        recipients = subscription.members_old
    else:
        recipients = subscription.members
    recipients.add(recipient)
    subscription.save()


def replace_subscription_types(subscription, selected_types):
    # always replace future sub types
    through_classes = [TFSST]
    # replace the current sub types as well, if the subscription is not active yet
    if subscription.state == 'waiting':
        through_classes.append(TSST)
    for through_class in through_classes:
        through_class.objects.filter(subscription=subscription).delete()
        through_class.objects.bulk_create(
            itertools.chain(*[[through_class(subscription=subscription, type=sub_type)] * amount
                              for sub_type, amount in selected_types.items()])
        )


def cancel_sub(subscription, end_date, message):
    if subscription.active is True and subscription.canceled is False:
        subscription.canceled = True
        subscription.end_date = end_date
        subscription.save()

        AdminNotification.subscription_canceled(subscription, message)
    elif subscription.active is False and subscription.deactivation_date is None:
        subscription.delete()


def cancel_extra_sub(extra):
    if extra.active is True:
        extra.canceled = True
        extra.save()
    elif extra.active is False and extra.deactivation_date is None:
        extra.delete()


def cancel_share(share, now, end_date):
    if share.paid_date is None:
        share.delete()
    else:
        share.cancelled_date = now
        share.termination_date = end_date
        share.save()
