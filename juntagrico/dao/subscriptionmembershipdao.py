from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipDao:

    @staticmethod
    def get_other_waiting_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription)\
            .filter(subscription__activation_date__isnull=True)\
            .filter(member=member)

    @staticmethod
    def get_other_active_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription)\
            .filter(subscription__activation_date__isnull=False,
                    subscription__cancellation_date__isnull=True,
                    subscription__deactivation_date__isnull=True)\
            .filter(member=member)

    @staticmethod
    def get_all_for_subscription(subscription):
        return SubscriptionMembership.objects.filter(subscription=subscription)
