from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.util.temporal import weekdays


depot_dict_generator = {
    'subscriptions': SubscriptionDao.all_active_subscritions,
    'products': SubscriptionProductDao.get_all,
    'extra_sub_categories': ExtraSubscriptionCategoryDao.categories_for_depot_list_ordered,
    'depots': DepotDao.all_depots_order_by_code,
    'weekdays': lambda: {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in DepotDao.distinct_weekdays()},
    'messages': ListMessageDao.all_active
}


def generate_depot_dict(keys):
    depot_dict = {}
    for key in keys:
        depot_dict[key] = depot_dict_generator[key]()
    return depot_dict


def get_amountlist_dict():
    return generate_depot_dict(('subscriptions', 'products', 'extra_sub_categories', 'weekdays'))


def get_depotoverview_dict():
    return generate_depot_dict(('subscriptions', 'products', 'extra_sub_categories', 'depots', 'weekdays'))


def get_depotlist_dict():
    return generate_depot_dict(('subscriptions', 'products', 'extra_sub_categories', 'depots', 'messages'))
