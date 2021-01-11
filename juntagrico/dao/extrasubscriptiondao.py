from juntagrico.entity.extrasubs import ExtraSubscription
from juntagrico.util.models import q_activated, q_cancelled, q_deactivated, q_isactive


class ExtraSubscriptionDao:

    @staticmethod
    def all_extra_subs():
        return ExtraSubscription.objects.all()

    @staticmethod
    def canceled_extra_subs():
        return ExtraSubscription.objects.filter(q_activated() & q_cancelled() & ~q_deactivated())

    @staticmethod
    def waiting_extra_subs():
        return ExtraSubscription.objects.filter(~q_activated())

    @staticmethod
    def all_active_extrasubscritions():
        return ExtraSubscription.objects.filter(q_isactive())

    @staticmethod
    def future_extrasubscriptions():
        return ExtraSubscription.objects.filter(~q_cancelled() & ~q_deactivated()).filter(deactivation_date=None)

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
