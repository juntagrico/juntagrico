from functools import partial

#from django.db.models import Q

from my_ortoloco.models import *


class Filter(object):
    all_filters = []

    def __init__(self, name, q):
        self.name = name
        def safe_q(*args):
            try:
                return q(*args)
            except Exception:
                return False
        self.q = safe_q
        self.all_filters.append(self)

    def get(self):
        yield self.name, self.q

    @classmethod
    def get_all(cls):
        res = []
        for instance in cls.all_filters:
            res.extend(instance.get())
        return res

    @classmethod
    def get_names(cls):
        for name, q in cls.get_all():
            yield name

    @classmethod
    def execute(cls, names, op):
        if op == "OR":
            aggregate = any
        elif op == "AND":
            aggregate = all

        d = dict(cls.get_all())
        filter_funcs = [d[name] for name in names]
        return [loco for loco in Loco.objects.all()
                if aggregate(f(loco) for f in filter_funcs)]


    @classmethod
    def format_data(cls, queryset, formatter):
        return [formatter(obj) for obj in queryset]


class FilterGen(Filter):
    def __init__(self, name_func, q_func, parameter_func):
        Filter.__init__(self, name_func, q_func)
        self.parameter_func = parameter_func

    def get(self):
        for p in self.parameter_func():
            yield self.name(p), partial(self.q, p)
        


FilterGen(lambda depot: "Depot {0}".format(depot.name),
          lambda depot, loco: loco.abo.depot==depot,
          Depot.objects.all)

Filter("Alle mit Abo", lambda loco: loco.abo)
Filter("Alle ohne Abo", lambda loco: not loco.abo)

Filter("Anteilscheinbesitzer",
       lambda loco: loco.user.anteilschein_set.exists())
Filter("Nicht Anteilscheinbesitzer",
       lambda loco: not loco.user.anteilschein_set.exists())

Filter("kleines Abo", lambda loco: loco.abo.kleine_abos())
Filter("grosses Abo", lambda loco: loco.abo.grosse_abos())
Filter("Hausabo", lambda loco: loco.abo.haus_abos())


FilterGen(lambda za: u"Zusatzabo {0}".format(za.name),
          lambda za, loco: za.abo_set.filter(id=loco.abo.id),
          ExtraAboType.objects.all)

FilterGen(lambda bereich: u"Taetigkeitsbereich {0}".format(bereich.name),
          lambda bereich, loco: bereich.users.filter(id=loco.user.id),
          Taetigkeitsbereich.objects.all)
