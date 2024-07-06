from juntagrico.entity.delivery import Delivery


class DeliveryDao:

    @staticmethod
    def deliveries_by_subscription(subscription):
        if subscription is not None:
            return Delivery.objects.all().order_by("-delivery_date").\
                filter(tour=subscription.depot.tour).\
                filter(subscription_size__types__subscription_parts__in=subscription.active_parts.all()).distinct()
        return Delivery.objects.none()
