from functools import partial

from juntagrico.models import *


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
        return [member for member in Member.objects.all()
                if aggregate(f(member) for f in filter_funcs)]


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
        


FilterGen(lambda depot: u"Depot {0}".format(depot.name),
          lambda depot, member: member.abo.depot == depot,
          Depot.objects.all)

Filter("Alle mit Abo", lambda member: member.abo)
Filter("Alle ohne Abo", lambda member: not member.abo)

Filter("Anteilscheinbesitzer",
       lambda member: member.user.share_set.exists())
Filter("Nicht Anteilscheinbesitzer",
       lambda member: not member.user.share_set.exists())

Filter("kleines Abo", lambda member: member.abo.small_abos)
Filter("grosses Abo", lambda member: member.abo.big_abos())
Filter("Hausabo", lambda member: member.abo.house_abos())


FilterGen(lambda za: u"Zusatzabo {0}".format(za.name),
          lambda za, member: za.abo_set.filter(id=member.abo.id),
          ExtraAboType.objects.all)

FilterGen(lambda activityarea: u"Taetigkeitsbereich {0}".format(activityarea.name),
          lambda activityarea, member: activityarea.users.filter(id=member.user.id),
          ActivityArea.objects.all)
