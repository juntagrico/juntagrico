from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipDao:

    @staticmethod
    def get_other_waiting_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription)\
            .filter(join_date__isnull=True)\
            .filter(member=member)

    @staticmethod
    def get_other_active_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription)\
            .filter(join_date__isnull=False,
                    leave_date__isnull=True)\
            .filter(member=member)

    @staticmethod
    def get_all_for_subscription(subscription):
        return SubscriptionMembership.objects.filter(subscription=subscription)
