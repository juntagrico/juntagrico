from polymorphic.query import PolymorphicQuerySet
from juntagrico.util.models import q_deactivated, q_activated, q_cancelled, q_isactive


class SubscriptionQuerySet(PolymorphicQuerySet):
    def waiting(self):
        return self.filter(~q_activated()).order_by('start_date')

    def active(self):
        return self.filter(q_isactive())

    def cancelled(self):
        return self.filter(q_cancelled() & ~q_deactivated()).order_by('end_date')

    def future(self):
        """ not cancelled """
        return self.filter(~q_cancelled())

    def in_depot(self, depot):
        return self.filter(depot=depot)

    def with_future_depot(self):
        return self.exclude(future_depot__isnull=True)
