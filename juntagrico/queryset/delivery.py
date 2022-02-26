from django.db.models import QuerySet


class DeliveryQuerySet(QuerySet):
    def by_subscription(self, subscription):
        if subscription is None:
            return self.none()
        return self.filter(
            delivery_date__iso_week_day=subscription.depot.weekday,
            subscription_size__types__subscriptions=subscription
        ).order_by("-delivery_date")
