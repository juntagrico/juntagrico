from juntagrico.entity.extrasubs import ExtraSubscription
from juntagrico.util.models import q_active, q_cancelled, q_deactivated


class ExtraSubscriptionDao:

    @staticmethod
    def all_extra_subs():
        return ExtraSubscription.objects.all()

    @staticmethod
    def canceled_extra_subs():
        return ExtraSubscription.objects.filter(q_active & q_cancelled & ~q_deactivated)

    @staticmethod
    def waiting_extra_subs():
        return ExtraSubscription.objects.filter(~q_active)

    @staticmethod
    def extrasubscriptions_by_date(fromdate, tilldate):
        """
        subscriptions that are active in a certain period.
        all subscriptions except those that ended before or
        started after the date range.
        """
        return ExtraSubscription.objects.\
            exclude(deactivation_date__lt=fromdate).\
            exclude(activation_date__gt=tilldate)
