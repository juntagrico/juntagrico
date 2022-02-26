from django.db.models import QuerySet


class JobTypeQuerySet(QuerySet):
    def visible(self):
        return self.filter(visible=True)

    def of_coordinator(self, member):
        return self.filter(activityarea__coordinator=member)
