from django.db.models import QuerySet

from juntagrico.util.temporal import weekdays


class DepotQueryset(QuerySet):
    def visible(self):
        return self.filter(visible=True)

    def for_depot_list(self):
        return self.filter(depot_list=True)

    def weekdays(self):
        return {
            weekdays[weekday]: weekday
            for weekday in self.order_by('weekday').values_list('weekday', flat=True).distinct()
        }

    def map_info(self):
        return [depot.map_info for depot in self]
