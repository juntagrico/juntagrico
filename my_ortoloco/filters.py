from django.db.models import Q

from my_ortoloco.models import *





class Filter(object):
    all_filters = []

    def __init__(self, name, q):
        self.name = name
        self.q = q
        self.all_filters.append(self)

    def get(self):
        yield self.name, self.q

    @classmethod
    def get_all(cls):
        res = []
        for instance in cls.all_filters:
            res.extend(instance.get())
        return res


class FilterList(Filter):
    def __init__(self, name_func, q_func, parameter_func):
        Filter.__init__(self, name_func, q_func)
        self.parameter_func = parameter_func

    def get(self):
        for p in self.parameter_func():
            yield self.name(p), self.q(p)
        



Filter("staff", Q(user__is_staff=True))
FilterList(lambda depot: "Depot %s" %depot.name,
           lambda depot: Q(abo__depot=depot), 
           Depot.objects.all)
