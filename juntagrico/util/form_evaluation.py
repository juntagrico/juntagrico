from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao


def selected_subscription_types(post_data):
    return {
        sub_type: int(
            post_data.get('amount[' + str(sub_type.id) + ']', 0)
        ) for sub_type in SubscriptionTypeDao.get_all()
    }
