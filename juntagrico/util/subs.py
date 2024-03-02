from juntagrico.dao.subscriptiondao import SubscriptionDao


def activate_future_depots():
    for subscription in SubscriptionDao.subscritions_with_future_depots():
        subscription.activate_future_depot()
