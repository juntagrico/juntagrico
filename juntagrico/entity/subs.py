# encoding: utf-8

from django.db import models

from juntagrico.dao.sharedao import ShareDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao

from juntagrico.util.temporal import *

from juntagrico.entity.billing import *

class SubscriptionSize(models.Model):
    """
    Subscription sizes
    """
    name = models.CharField("Name", max_length=100, unique=True)
    long_name = models.CharField("Langer Name", max_length=100, unique=True)
    size = models.PositiveIntegerField("Grösse", unique=True)
    shares = models.PositiveIntegerField("Anz benötigter Anteilsscheine")
    required_assignments = models.PositiveIntegerField("Anz benötigter Arbeitseinsätze")
    price = models.PositiveIntegerField("Preis")
    depot_list = models.BooleanField('Sichtbar auf Depotliste', default=True)
    description = models.TextField("Beschreibung", max_length=1000, blank=True)
    

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Abo Grösse'
        verbose_name_plural = 'Abo Grössen'


class Subscription(Billable):
    """
    One Subscription that may be shared among several people.
    """
    depot = models.ForeignKey("Depot", on_delete=models.PROTECT, related_name="subscription_set")
    future_depot = models.ForeignKey("Depot", on_delete=models.PROTECT, related_name="future_subscription_set", null=True,
                                     blank=True, )
    size = models.PositiveIntegerField(default=1)
    future_size = models.PositiveIntegerField("Zukuenftige Groesse", default=1)
    primary_member = models.ForeignKey("Member", related_name="subscription_primary", null=True, blank=True,
                                       on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    activation_date = models.DateField("Aktivierungssdatum", null=True, blank=True)
    deactivation_date = models.DateField("Deaktivierungssdatum", null=True, blank=True)
    creation_date = models.DateField("Erstellungsdatum", null=True, blank=True, auto_now_add=True)
    start_date = models.DateField("Gewünschtes Startdatum", null=False, default=start_of_next_business_year)
    old_active = None
    sizes_cache = {}

    def __unicode__(self):
        namelist = ["1 Einheit" if self.size == 1 else "%d Einheiten" % self.size]
        namelist.extend(extra.type.name for extra in self.extra_subscriptions.all())
        return u"Abo (%s) %s" % (" + ".join(namelist), self.id)

    def overview(self):
        namelist = ["1 Einheit" if self.size == 1 else "%d Einheiten" % self.size]
        namelist.extend(extra.type.name for extra in self.extra_subscriptions.all())
        return u"%s" % (" + ".join(namelist))

    def recipients_names(self):
        members = self.members.all()
        return ", ".join(unicode(member) for member in members)

    def other_recipients_names(self):
        members = self.recipients().exclude(email=self.primary_member.email)
        return ", ".join(unicode(member) for member in members)

    def recipients(self):
        return self.members.all()

    def primary_member_nullsave(self):
        member = self.primary_member
        return unicode(member) if member is not None else ""

    @property
    def extra_subscriptions(self):
        return self.extra_subscription_set.filter(active=True)

    @property
    def paid_shares(self):
        return ShareDao.paid_shares(self).count()

    @property
    def future_extra_subscriptions(self):
        return self.extra_subscription_set.filter(
            Q(active=False, deactivation_date=None) | Q(active=True, canceled=False))

    @staticmethod
    def fill_sizes_cache():
        list = []
        map = {}
        index = 0
        for size in SubscriptionSizeDao.all_sizes_ordered():
            list.append(size.size)
            map[size.name] = index
            index += 1
        Subscription.sizes_cache = {'list': list,
                                    'map': map,
                                    }

    def subscription_amount(self, subscription_name):
        return self.calc_subscritpion_amount(self.size, subscription_name)

    def subscription_amount_future(self, subscription_name):
        return self.calc_subscritpion_amount(self.future_size, subscription_name)

    @staticmethod
    def calc_subscritpion_amount(size, subscription_name):
        if Subscription.sizes_cache == {}:
            Subscription.fill_sizes_cache()
        if Subscription.sizes_cache['list'].__len__ == 1:
            return size / Subscription.sizes_cache['list'][0]
        index = Subscription.sizes_cache['map'][subscription_name]
        if index == len(Subscription.sizes_cache['list']) - 1:
            return int(size / Subscription.sizes_cache['list'][index])
        return int((size % Subscription.sizes_cache['list'][index + 1]) / Subscription.sizes_cache['list'][index])

    @staticmethod
    def next_extra_change_date():
        month = int(time.strftime("%m"))
        if month >= 7:
            next_extra = timezone.date(day=1, month=1, year=timezone.date.today().year + 1)
        else:
            next_extra = timezone.date(day=1, month=7, year=timezone.date.today().year)
        return next_extra

    @staticmethod
    def get_size_name(size=0):
        size_names = []
        for sub_size in SubscriptionSizeDao.all_sizes_ordered():
            amount = Subscription.calc_subscritpion_amount(size, sub_size.name)
            if amount > 0:
                size_names.append(sub_size.long_name + " : " + amount)
        if len(size_names) > 0:
            return ', '.join(size_names)
        return "kein Abo"
        
    def required_assignments(self):
        result = 0
        for sub_size in SubscriptionSizeDao.all_sizes_ordered():
            amount = Subscription.calc_subscritpion_amount(self.size, sub_size.name)
            resukt += sub_size.required_assignments * amount
        return result

    @property
    def size_name(self):
        return Subscription.get_size_name(size=self.size)

    @property
    def future_size_name(self):
        return Subscription.get_size_name(size=self.future_size)

    def extra_subscription(self, code):
        return len(self.extra_subscriptions.all().filter(type__name=code)) > 0

    def clean(self):
        if self.old_active != self.active and self.deactivation_date is not None:
            raise ValidationError(u'Deaktivierte Abos koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active is False and instance.deactivation_date is None:
            instance.activation_date = timezone.now().date()
        elif instance.old_active != instance.active and instance.old_active is True and instance.deactivation_date is None:
            instance.deactivation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active

    @classmethod
    def pre_delete(cls, sender, instance, **kwds):
        for member in instance.recipients():
            member.subscription = None
            member.save()

    class Meta:
        verbose_name = "Abo"
        verbose_name_plural = "Abos"
        permissions = (('can_filter_subscriptions', 'Benutzer kann Abos filtern'),)