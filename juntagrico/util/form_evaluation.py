from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao


def selected_subscription_types(post_data):
    return {
        sub_type: int(
            post_data.get('amount[' + str(sub_type.id) + ']',  # if multi selection
                          int(post_data.get('subscription', -1)) == sub_type.id)  # if single selection
        ) for sub_type in SubscriptionTypeDao.get_all()
    }
