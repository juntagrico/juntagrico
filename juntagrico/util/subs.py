from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.mailer import membernotification


def activate_future_depots():
    for subscription in SubscriptionDao.subscritions_with_future_depots():
        subscription.depot = subscription.future_depot
        subscription.future_depot = None
        subscription.save()
        emails = []
        for member in subscription.recipients:
            emails.append(member.email)
        membernotification.depot_changed(emails, subscription.depot)
