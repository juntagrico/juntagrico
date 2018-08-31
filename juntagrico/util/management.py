import hashlib
import random
import string

from juntagrico.models import Share, Subscription, TSST, TFSST
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.mailer import send_welcome_mail
from juntagrico.mailer import send_been_added_to_subscription
from juntagrico.mailer import send_share_created_mail


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(
        random.choice(chars) for x in range(size))


def create_subscription(start_date, depot, selectedsubscription):
    subscription = Subscription()
    subscription.start_date = start_date
    subscription.depot = depot
    subscription.save()
    type = SubscriptionTypeDao.get_by_id(int(selectedsubscription))[0]
    TSST.objects.create(type=type, subscription=subscription)
    TFSST.objects.create(type=type, subscription=subscription)
    return subscription


def create_member(member, subscription, main_member=None, shares=None):
    if subscription is not None:
        if subscription.state == 'waiting':
            member.future_subscription = subscription
        elif subscription.state == 'inactive':
            member.old_subscriptions.add(subscription)
        else:
            member.subscription = subscription
    member.future_subscription = subscription
    member.save()
    password = password_generator()
    member.user.set_password(password)
    member.user.save()
    key = (member.email + str(member.id)).encode('utf8')
    hash = hashlib.sha1(key).hexdigest()
    if main_member is None:
        send_welcome_mail(member.email, password, hash, subscription)
    else:
        name = main_member.get_name()
        email = member.email
        send_been_added_to_subscription(email, password, hash, name, shares)


def update_member(member, subscription, main_member=None, shares=None):
    if subscription is not None:
        if subscription.state == 'waiting':
            member.future_subscription = subscription
        elif subscription.state == 'inactive':
            member.old_subscriptions.add(subscription)
        else:
            member.subscription = subscription
    member.save()
    if main_member is not None:
        name = main_member.get_name()
        email = member.email
        send_been_added_to_subscription(email, None, None, name, shares, False)


def create_share(member):
    share = Share.objects.create(member=member)
    send_share_created_mail(member, share)
