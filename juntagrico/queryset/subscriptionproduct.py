from django.db.models import Manager, QuerySet


class ProductQuerySet(QuerySet):
    def visible(self):
        return self.filter(sizes__visible=True).distinct()

    def for_depot_list(self):
        return self.filter(sizes__depot_list=True).distinct()


class NormalProductManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_extra=False)


class ExtraProductManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_extra=True)
