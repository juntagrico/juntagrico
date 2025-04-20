from django.db.models.functions import Ceil

from juntagrico.queryset.subscription import SubscriptionQuerySet


# Example for custom rounding of required assignments
def my_rounding(number):
    return Ceil(number*2)/2


SubscriptionQuerySet._assignment_rounding = staticmethod(my_rounding)
