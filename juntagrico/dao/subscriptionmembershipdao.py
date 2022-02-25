from juntagrico.entity.member import SubscriptionMembership, q_joined_subscription, q_left_subscription


# TODO: remove these, by rewriting the consistency checks
class SubscriptionMembershipDao:
    @staticmethod
    def get_other_waiting_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(~q_joined_subscription()) \
            .filter(member=member)

    @staticmethod
    def get_other_active_for_member(member, subscription, asof=None):
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(q_joined_subscription() & ~q_left_subscription(asof)) \
            .filter(member=member)
