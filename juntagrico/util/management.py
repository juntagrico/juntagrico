import hashlib
import random
import string

from juntagrico.models import *
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(
    random.choice(chars) for x in range(size))



def create_subscription(start_date, depot, selectedsubscription):       
    subscription = Subscription()
    subscription.start_date = start_date
    subscription.depot = depot
    subscription.save()
    types = list((type for type in SubscriptionTypeDao.get_by_id(int(selectedsubscription))))                    
    TSST.objects.create(type=types[0], subscription=subscription)                
    TFSST.objects.create(type=types[0], subscription=subscription)
    return subscription

    
def create_member(member, subscription, main_member=None, shares=None):
    member.future_subscription = subscription
    member.save()
    password = password_generator()
    member.user.set_password(password)
    member.user.save()
    hash = hashlib.sha1((member.email + str(member.id)).encode('utf8')).hexdigest()
    if main_member is None:
        send_welcome_mail(member.email, password, hash, subscription)
    else:
        name = main_member.get_name()
        send_been_added_to_subscription(member.email, password, hash, name, shares)
       
       
def update_member(member, subscription, main_member=None, shares=None):
    member.future_subscription = subscription
    member.save()
    if main_member is not None:
        name = main_member.get_name()
        send_been_added_to_subscription(member.email, None, None, name, shares, False)
    
    
def create_share(member):
    share = Share.objects.create(member=member)
    send_share_created_mail(member, share)