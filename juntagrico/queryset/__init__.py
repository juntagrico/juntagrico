import datetime

from django.db.models import Q


def q_joined(on_date):
    return Q(subscriptionmembership__join_date__lte=on_date)


def q_not_left(on_date):
    return Q(subscriptionmembership__leave_date__gt=on_date) | Q(subscriptionmembership__leave_date=None)


class SubscriptionMembershipQuerySetMixin:
    """
    This is used by SubscriptionQueryset and MemberQuerySet and allows getting joining and joined subscription
    in either directions:
    subscription.members.joined()
    member.subscriptions.joined()
    """
    def joining(self, on_date=None):
        on_date = on_date or datetime.date.today()
        # note: using exclude here would exclude members that left another subscription
        return self.filter(q_not_left(on_date))

    def joined(self, on_date=None):
        on_date = on_date or datetime.date.today()
        # note: chaining filter() calls would yield too many results
        # https://docs.djangoproject.com/en/4.2/topics/db/queries/#spanning-multi-valued-relationships
        return self.filter(q_joined(on_date) & q_not_left(on_date))
