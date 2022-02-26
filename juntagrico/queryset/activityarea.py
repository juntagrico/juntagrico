from django.db.models import QuerySet


class ActivityAreaQuerySet(QuerySet):
    def visible(self):
        return self.filter(hidden=False)

    def core(self):
        return self.filter(core=True)

    def sorted(self):
        return self.order_by('-core', 'name')

    def auto_added(self):
        return self.filter(auto_add_new_members=True)
