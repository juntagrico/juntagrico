import hashlib
import itertools
import random
import string

from juntagrico.models import Share, Subscription, TSST, TFSST
from juntagrico.mailer import send_welcome_mail
from juntagrico.mailer import send_been_added_to_subscription
from juntagrico.mailer import send_share_created_mail
from juntagrico.config import Config


def password_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(
        random.choice(chars) for _ in range(size))


def create_subscription(start_date, depot, selected_subscriptions):
    subscription = Subscription()
    subscription.start_date = start_date
    subscription.depot = depot
    subscription.save()
    replace_subscription_types(subscription, selected_subscriptions)
    return subscription


def create_or_update_member(member, subscription, shares=None, main_member=None):
    create = member.pk is None
    # add member to subscription
    add_subscription_to_member(member, subscription)
    member.save()
    # create shares for member
    create_share(member, shares)
    # generate password if member is new
    password = None
    member_hash = None
    if create:
        password = password_generator()
        member.user.set_password(password)
        member.user.save()
        key = (member.email + str(member.id)).encode('utf8')
        member_hash = hashlib.sha1(key).hexdigest()
        if main_member is None:
            send_welcome_mail(member.email, password, member_hash, subscription)
    # notify main member of subscription
    if main_member is not None:
        name = main_member.get_name()
        email = member.email
        send_been_added_to_subscription(email, password, member_hash, name, shares, create)


def create_share(member, amount=1):
    if amount and Config.enable_shares():
        for i in range(amount):
            share = Share.objects.create(member=member)
            send_share_created_mail(member, share)


def add_subscription_to_member(member, subscription):
    if subscription is not None:
        if subscription.state == 'waiting':
            member.future_subscription = subscription
        elif subscription.state == 'inactive':
            member.old_subscriptions.add(subscription)
        else:
            member.subscription = subscription


def replace_subscription_types(subscription, selected_types, _obj=TFSST):
    """
    Deletes all types of a subscription and replace them with the types and amounts given by selected_types
    :param subscription: The Subscription object whose types should be replaced
    :param selected_types: dictionary of subscription types as key and amount as value
    :param _obj: for internal use
    :type _obj: type(TFSST) or type(TSST)
    :return: None
    """
    _obj.objects.filter(subscription=subscription).delete()
    _obj.objects.bulk_create(
        itertools.chain(*[[_obj(subscription=subscription, type=sub_type)] * amount
                          for sub_type, amount in selected_types.items()])
    )
    # replace the current sub types as well, if the subscription is not active yet:
    if _obj is TFSST and subscription.state == 'waiting':
        replace_subscription_types(subscription, selected_types, TSST)
