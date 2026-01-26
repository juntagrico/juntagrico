from django.db.models import QuerySet, F


class TourQueryset(QuerySet):
    def sort_by_weekday(self):
        return self.order_by(F('weekday').asc(nulls_last=True))
