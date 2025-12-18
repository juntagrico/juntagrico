import datetime

from django.db.models import QuerySet, F, Q, Count


class SubscriptionTypeQueryset(QuerySet):
    def normal(self):
        return self.filter(is_extra=False)

    def is_extra(self):
        return self.filter(is_extra=True)

    def visible(self):
        return self.filter(visible=True, bundle__category__isnull=False)

    def with_active_or_future_parts(self):
        return self.filter(
            Q(subscription_parts__deactivation_date=None) |
            Q(subscription_parts__deactivation_date__gte=datetime.date.today())
        )

    def annotate_content(self):
        return self.annotate(
            bundle_name=F('bundle__long_name'),
            category_name=F('bundle__category__name'),
            amount=Count('bundle_id')
        )

    def can_change(self):
        return self.normal().visible().count() > 1


class SubscriptionProductQueryset(QuerySet):
    def on_depot_list(self):
        return self.filter(sizes__show_on_depot_list=True, sizes__bundles__isnull=False).distinct()


class ProductSizeQueryset(QuerySet):
    def sorted(self):
        return self.order_by('units')

    def on_depot_list(self):
        return self.filter(show_on_depot_list=True, bundles__isnull=False).distinct()
