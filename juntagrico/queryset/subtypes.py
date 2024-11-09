import datetime

from django.db.models import QuerySet, Sum, F, Q


class SubscriptionTypeQueryset(QuerySet):
    def normal(self):
        return self.filter(size__product__is_extra=False)

    def is_extra(self):
        return self.filter(size__product__is_extra=True)

    def visible(self):
        return self.filter(visible=True, size__visible=True)

    def on_depot_list(self):
        return self.filter(size__depot_list=True)

    def with_active_or_future_parts(self):
        return self.filter(
            Q(subscription_parts__deactivation_date=None) |
            Q(subscription_parts__deactivation_date__gte=datetime.date.today())
        )

    def annotate_content(self):
        return self.annotate(
            size_units=F('size__units'),
            size_name=F('size__name'),
            product_name=F('size__product__name'),
            size_sum=Sum('size_units')
        )
