from django.db.models import QuerySet


class SubscriptionTypeQueryset(QuerySet):
    def normal(self):
        return self.filter(size__product__is_extra=False)

    def is_extra(self):
        return self.filter(size__product__is_extra=True)

    def visible(self, ):
        return self.filter(visible=True, size__visible=True)
