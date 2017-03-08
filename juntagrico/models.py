# encoding: utf-8

import datetime
import time

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals, Q
from django.utils import timezone
from polymorphic.models import PolymorphicModel

import helpers
from config import *
import model_audit
from juntagrico.mailer import *


class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    code = models.CharField("Code", max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField("Depot Name", max_length=100, unique=True)
    contact = models.ForeignKey("Member", on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField("Wochentag", choices=helpers.weekday_choices)
    latitude = models.CharField("Latitude", max_length=100, default="")
    longitude = models.CharField("Longitude", max_length=100, default="")

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)

    description = models.TextField("Beschreibung", max_length=1000, default="")

    overview_cache = None
    subscription_cache = None

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    def active_subscriptions(self):
        return self.subscription_set.filter(active=True)

    @property
    def weekday_name(self):
        day = "Unbekannt"
        if 8 > self.weekday > 0:
            day = helpers.weekdays[self.weekday]
        return day

    @staticmethod
    def subscription_amounts(subscriptions, name):
        amount = 0
        for subscription in subscriptions.all():
            amount += subscription.subscription_amount(name)
        return amount

    @staticmethod
    def extra_subscription(subscriptions, code):
        amount = 0
        for subscription in subscriptions.all():
            amount += len(subscription.extra_subscriptions.all().filter(type__name=code))
        return amount

    def fill_overview_cache(self):
        self.fill_active_subscription_cache()
        self.overview_cache = []
        for subscription_size in SubscriptionSize.objects.filter(depot_list=True).order_by('size'):
            self.overview_cache.append(self.subscription_amounts(self.subscription_cache, subscription_size.name))
        for category in ExtraSubscriptionCategory.objects.all().order_by("sort_order"):
            for extra_subscription in ExtraSubscriptionType.objects.all().filter(category=category).order_by("sort_order"):
                code = extra_subscription.name
                self.overview_cache.append(self.extra_subscription(self.subscription_cache, code))

    def fill_active_subscription_cache(self):
        self.subscription_cache = self.active_subscriptions()

    class Meta:
        verbose_name = "Depot"
        verbose_name_plural = "Depots"
        permissions = (('is_depot_admin', 'Benutzer ist Depot Abodmin'),)


class Billable(PolymorphicModel):
    """
    Parent type for billables.
    """

    class Meta:
        verbose_name = 'Verrechenbare Einheit'
        verbose_name_plural = 'Verrechenbare Einhaiten'


class Bill(models.Model):
    """
    Aboctuall Bill for billables
    """
    billable = models.ForeignKey(Billable, related_name="bills", null=False, blank=False,
                                 on_delete=models.PROTECT)
    paid = models.BooleanField("bezahlt", default=False)
    bill_date = models.DateField("Aboktivierungssdatum", null=True, blank=True)
    ref_number = models.CharField("Referenznummer", max_length=30, unique=True)
    amount = models.FloatField("Betrag", null=False, blank=False)

    def __unicode__(self):
        return u"%s %s" % (self.ref_number)

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"


class Payment(models.Model):
    """
    Payment for bill
    """
    bill = models.ForeignKey(Bill, related_name="payments", null=False, blank=False,
                             on_delete=models.PROTECT)
    paid_date = models.DateField("Bezahldatum", null=True, blank=True)
    amount = models.FloatField("Betrag", null=False, blank=False)

    def __unicode__(self):
        return u"%s %s" % (self.ref_number)

    class Meta:
        verbose_name = "Zahlung"
        verbose_name_plural = "Zahlung"


class ExtraSubscriptionType(models.Model):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    size = models.CharField("Groesse (gross,4, ...)", max_length=100, default="")
    description = models.TextField("Beschreibung", max_length=1000)
    sort_order = models.FloatField("Groesse zum Sortieren", default=1.0)
    category = models.ForeignKey("ExtraAbo$oCategory", related_name="category", null=True, blank=True,
                                 on_delete=models.PROTECT)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo$o-Typ"
        verbose_name_plural = "Zusatz-Abo$o-Typen"


class ExtraSubscriptionCategory(models.Model):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, blank=True)
    sort_order = models.FloatField("Nummer zum Sortieren", default=1.0)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo$o-Kategorie"
        verbose_name_plural = "Zusatz-Abo$o-Kategorien"


class ExtraSubscription(Billable):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    main_subscription = models.ForeignKey("Abo$o", related_name="extra_subscription_set", null=False, blank=False,
                                 on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    canceled = models.BooleanField("gekündigt", default=False)
    activation_date = models.DateField("Aboktivierungssdatum", null=True, blank=True)
    deactivation_date = models.DateField("Deaktivierungssdatum", null=True, blank=True)
    type = models.ForeignKey(ExtraSubscriptionType, related_name="extra_subscriptions", null=False, blank=False,
                             on_delete=models.PROTECT)

    old_active = None

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active is False and instance.deactivation_date is None:
            instance.activation_date = timezone.now().date()
        elif instance.old_active != instance.active and instance.old_active is True and instance.deactivation_date is None:
            instance.deactivation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active

    def __unicode__(self):
        return u"%s %s" % (self.id, self.type.name)

    class Meta:
        verbose_name = "Zusatz-Abo$o"
        verbose_name_plural = "Zusatz-Abo$os"


class SubscriptionSize(models.Model):
    """
    Subscription sizes
    """
    name = models.CharField("Name", max_length=100, unique=True)
    long_name = models.CharField("Langer Name", max_length=100, unique=True)
    size = models.PositiveIntegerField("Grösse", unique=True)
    shares = models.PositiveIntegerField("Abonz benötigter Abonteilsscheine")
    depot_list = models.BooleanField('Sichtbar auf Depotliste', default=True)
    description = models.TextField("Beschreibung", max_length=1000, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Abobo Grösse'
        verbose_name_plural = 'Abobo Grössen'


class Subscription(Billable):
    """
    One Subscription that may be shared among several people.
    """
    depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name="subscription_set")
    future_depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name="future_subscription_set", null=True,
                                     blank=True, )
    size = models.PositiveIntegerField(default=1)
    future_size = models.PositiveIntegerField("Zukuenftige Groesse", default=1)
    primary_member = models.ForeignKey("Member", related_name="subscription_primary", null=True, blank=True,
                                       on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    activation_date = models.DateField("Aboktivierungssdatum", null=True, blank=True)
    deactivation_date = models.DateField("Deaktivierungssdatum", null=True, blank=True)
    creation_date = models.DateField("Erstellungsdatum", null=True, blank=True, auto_now_add=True)
    start_date = models.DateField("Gewünschtes Startdatum", null=False, default=start_of_next_year)
    old_active = None
    sizes_cache = {}

    def __unicode__(self):
        namelist = ["1 Einheit" if self.size == 1 else "%d Einheiten" % self.size]
        namelist.extend(extra.type.name for extra in self.extra_subscriptions.all())
        return u"Abo$o (%s) %s" % (" + ".join(namelist), self.id)

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
        return Share.objects.filter(member__in=self.members.all()).filter(paid_date__isnull=False).filter(
            cancelled_date__isnull=True).count()

    @property
    def future_extra_subscriptions(self):
        return self.extra_subscription_set.filter(Q(active=False, deactivation_date=None) | Q(active=True, canceled=False))

    @staticmethod
    def fill_sizes_cache():
        list = []
        map = {}
        index = 0
        for size in SubscriptionSize.objects.order_by('size'):
            list.append(size.size)
            map[size.name] = index
            index = index + 1
        Subscription.sizes_cache = {'list': list,
                           'map': map,
                           }

    def subscription_amount(self, subscription_name):
        if Subscription.sizes_cache == {}:
            Subscription.fill_sizes_cache()
        if Subscription.sizes_cache['list'].__len__ == 1:
            return self.size / Subscription.sizes_cache['list'][0]
        index = Subscription.sizes_cache['map'][subscription_name]
        if index == len(Subscription.sizes_cache['list']) - 1:
            return int(self.size / Subscription.sizes_cache['list'][index])
        return int((self.size % Subscription.sizes_cache['list'][index + 1]) / Subscription.sizes_cache['list'][index])

    def subscription_amount_future(self, subscription_name):
        if Subscription.sizes_cache == {}:
            Subscription.fill_sizes_cache()
        if Subscription.sizes_cache['list'].__len__ == 1:
            return self.future_size / Subscription.sizes_cache['list'][0]
        index = Subscription.sizes_cache['map'][subscription_name]
        if index == len(Subscription.sizes_cache['list']) - 1:
            return int(self.future_size / Subscription.sizes_cache['list'][index])
        return int((self.future_size % Subscription.sizes_cache['list'][index + 1]) / Subscription.sizes_cache['list'][index])

    @staticmethod
    def next_extra_change_date():
        month = int(time.strftime("%m"))
        if month >= 7:
            next_extra = datetime.date(day=1, month=1, year=datetime.date.today().year + 1)
        else:
            next_extra = datetime.date(day=1, month=7, year=datetime.date.today().year)
        return next_extra

    @staticmethod
    def next_size_change_date():
        return datetime.date(day=1, month=1, year=datetime.date.today().year + 1)

    @staticmethod
    def get_size_name(size=0):
        if size == 1:
            return "Kleines Abo$o"
        elif size == 2:
            return "Grosses Abo$o"
        elif size == 10:
            return "Haus Abo$o"
        elif size == 3:
            return "Kleines + Grosses Abo$o"
        elif size == 4:
            return "2 Grosse Abo$os"
        else:
            return "Kein Abo$o"

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
            raise ValidationError(u'Deaktivierte Abobos koennen nicht wieder aktiviert werden', code='invalid')

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
        verbose_name = "Abo$o"
        verbose_name_plural = "Abo$os"
        permissions = (('can_filter_subscriptions', 'Benutzer kann Abobos filtern'),)


class Member(models.Model):
    """
    Abodditional fields for Django's default user class.
    """

    # user class is only used for logins, permissions, and other builtin django stuff
    # all user information should be stored in the Member model
    user = models.OneToOneField(User, related_name='member', null=True, blank=True)

    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)
    birthday = models.DateField("Geburtsdatum", null=True, blank=True)
    phone = models.CharField("Telefonnr", max_length=50)
    mobile_phone = models.CharField("Mobile", max_length=50, null=True, blank=True)

    subscription = models.ForeignKey(Subscription, related_name="members", null=True, blank=True,
                            on_delete=models.SET_NULL)

    confirmed = models.BooleanField("bestätigt", default=True)
    reachable_by_email = models.BooleanField("Kontaktierbar von der Job Seite aus", default=False)
    block_emails = models.BooleanField("keine emails", default=False)

    old_subscription = None

    def __unicode__(self):
        return self.get_name()

    @classmethod
    def create(cls, sender, instance, created, **kdws):
        """
        Callback to create corresponding member when new user is created.
        """
        if created:
            username = helpers.make_username(instance.first_name, instance.last_name, instance.email)
            user = User(username=username)
            user.save()
            user = User.objects.get(username=username)
            instance.user = user
            instance.save()

    @classmethod
    def post_delete(cls, sender, instance, **kwds):
        instance.user.delete()

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_subscription != instance.subscription and instance.subscription is None:
            instance.areas = ()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_subscription = None  # instance.subscription

    class Meta:
        verbose_name = Config.member_string()
        verbose_name_plural = Config.members_string()
        permissions = (('can_filter_members', 'Benutzer kann ' + Config.members_string() + ' filtern'),)

    def get_name(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def get_phone(self):
        if self.mobile_phone != "":
            return self.mobile_phone
        return self.phone


class Share(Billable):
    member = models.ForeignKey(Member, null=True, blank=True, on_delete=models.SET_NULL)
    paid_date = models.DateField("Bezahlt am", null=True, blank=True);
    issue_date = models.DateField("Abousgestellt am", null=True, blank=True);
    booking_date = models.DateField("Eingebucht am", null=True, blank=True);
    cancelled_date = models.DateField("Gekündigt am", null=True, blank=True);
    termination_date = models.DateField("Gekündigt auf", null=True, blank=True);
    payback_date = models.DateField("Zurückbezahlt am", null=True, blank=True);
    number = models.IntegerField("Abonteilschein Nummer", null=True, blank=True);
    notes = models.TextField("Notizen", max_length=1000, default="", blank=True)

    def __unicode__(self):
        return u"Abonteilschein #%s" % self.id

    class Meta:
        verbose_name = "Abonteilschein"
        verbose_name_plural = "Abonteilscheine"


class AboctivityAborea(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    core = models.BooleanField("Kernbereich", default=False)
    hidden = models.BooleanField("versteckt", default=False)
    coordinator = models.ForeignKey(Member, on_delete=models.PROTECT)
    members = models.ManyToManyField(Member, related_name="areas", blank=True)
    show_coordinator_phonenumber = models.BooleanField("Koordinator Tel Nr Veröffentlichen", default=False)

    def __unicode__(self):
        return u'%s' % self.name

    def contact(self):
        if self.show_coordinator_phonenumber is True:
            return self.coordinator.phone + "   " + self.coordinator.mobile_phone
        else:
            return self.coordinator.email

    class Meta:
        verbose_name = 'Tätigkeitsbereich'
        verbose_name_plural = 'Tätigkeitsbereiche'
        permissions = (('is_area_admin', 'Benutzer ist TätigkeitsbereichskoordinatorIn'),)


class AbobstractJobType(models.Model):
    """
    Abobstract type of job.
    """
    name = models.CharField("Name", max_length=100, unique=True)
    displayed_name = models.CharField("Abongezeigter Name", max_length=100, blank=True, null=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    activityarea = models.ForeignKey(AboctivityAborea, on_delete=models.PROTECT)
    duration = models.PositiveIntegerField("Dauer in Stunden")
    location = models.CharField("Ort", max_length=100, default="")

    def __unicode__(self):
        return u'%s - %s' % (self.activityarea, self.get_name())

    def get_name(self):
        if self.displayed_name is not None:
            return self.displayed_name
        return self.name

    class Meta:
        verbose_name = 'AbobstractJobart'
        verbose_name_plural = 'AbobstractJobarten'
        abstract = True


class JobType(AbobstractJobType):
    """
    Recuring type of job. do not add field here do it in the parent
    """

    class Meta:
        verbose_name = 'Jobart'
        verbose_name_plural = 'Jobarten'


class Job(PolymorphicModel):
    slots = models.PositiveIntegerField("Plaetze")
    time = models.DateTimeField()
    pinned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField("Reminder verschickt", default=False)
    canceled = models.BooleanField("abgesagt", default=False)
    old_canceled = None
    old_time = None

    @property
    def typeself):
        raise NotImplementedError

    def __unicode__(self):
        return u'Job #%s' % self.id

    def weekday_name(self):
        weekday = helpers.weekdays[self.time.isoweekday()]
        return weekday[:2]

    def time_stamp(self):
        return int(time.mktime(self.time.timetuple()) * 1000)

    def freie_plaetze(self):
        if not (self.slots is None):
            return self.slots - self.occupied_places()
        else:
            return 0

    def end_time(self):
        return self.time + datetime.timedelta(hours=self.typeduration)

    def start_time(self):
        return self.time

    def occupied_places(self):
        return self.assignments_set.count()

    def get_status_percentage(self):
        assignments = Abossignment.objects.filter(job_id=self.id)
        if self.slots < 1:
            return helpers.get_status_bean(100)
        return helpers.get_status_bean(assignments.count() * 100 / self.slots)

    def is_core(self):
        return self.typeactivityarea.core

    def clean(self):
        if self.old_canceled != self.canceled and self.old_canceled is True:
            raise ValidationError(u'Abobgesagte jobs koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_canceled != instance.canceled and instance.old_canceled is False:
            assignments = Abossignment.objects.filter(job_id=instance.id)
            emails = set()
            for assignment in assignments:
                emails.add(assignment.member.email)
            instance.slots = 0
            if len(emails) > 0:
                send_job_canceled(emails, instance, Config.server_url())
        if instance.old_time != instance.time:
            assignments = Abossignment.objects.filter(job_id=instance.id)
            emails = set()
            for assignment in assignments:
                emails.add(assignment.member.email)
            if len(emails) > 0:
                send_job_time_changed(emails, instance, Config.server_url())

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_time = instance.time
        instance.old_canceled = instance.canceled
        if instance.canceled:
            assignments = Abossignment.objects.filter(job_id=instance.id)
            assignments.delete()

    class Meta:
        verbose_name = 'AbobstractJob'
        verbose_name_plural = 'AbobstractJobs'


class RecuringJob(Job):
    type= models.ForeignKey(JobType, on_delete=models.PROTECT)

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'


class OneTimeJob(Job, AbobstractJobType):
    """
    One time job. Do not add Field here do it in the Parent class
    """

    @property
    def typeself):
        return self

    def __unicode__(self):
        return u'%s - %s' % (self.activityarea, self.get_name())

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = 'EinzelJob'
        verbose_name_plural = 'EinzelJobs'


class Abossignment(models.Model):
    """
    Single assignment (work unit).
    """
    job = models.ForeignKey(Job, on_delete=models.CAboSCAboDE)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    core_cache = models.BooleanField("Kernbereich", default=False)

    def __unicode__(self):
        return u'Abossignment #%s' % self.id

    def time(self):
        return self.job.time

    def is_core(self):
        return self.job.typeactivityarea.core

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        instance.core_cache = instance.is_core()

    class Meta:
        verbose_name = Config.assignment_string()
        verbose_name_plural = Config.assignments_string()


class MailTemplate(models.Model):
    """
    Mail template for rendering
    """
    name = models.CharField("Name", max_length=100, unique=True)
    template = models.TextField("Template", max_length=1000, default="")
    code = models.TextField("Code", max_length=1000, default="")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'MailTemplate'
        verbose_name_plural = 'MailTemplates'


class SpecialRoles(models.Model):
    """
    No instances should be created of this class it i just the place to create permissions
    like bookkeeper or operation group
    """

    class Meta:
        permissions = (('is_operations_group', 'Benutzer ist in der BG'),
                       ('is_book_keeper', 'Benutzer ist Buchhalter'),
                       ('can_send_mails', 'Benutzer kann im System Emails versenden'),
                       ('can_use_general_email', 'Benutzer kann General Email Abodresse verwenden'),)


# model_audit.m2m(Subscription.users)
model_audit.fk(Subscription.depot)
model_audit.fk(Share.member)

signals.post_save.connect(Member.create, sender=Member)
signals.post_delete.connect(Member.post_delete, sender=Member)
signals.pre_save.connect(Member.pre_save, sender=Member)
signals.post_init.connect(Member.post_init, sender=Member)
signals.pre_save.connect(Job.pre_save, sender=Job)
signals.post_init.connect(Job.post_init, sender=Job)
signals.pre_save.connect(RecuringJob.pre_save, sender=RecuringJob)
signals.post_init.connect(RecuringJob.post_init, sender=RecuringJob)
signals.pre_save.connect(OneTimeJob.pre_save, sender=OneTimeJob)
signals.post_init.connect(OneTimeJob.post_init, sender=OneTimeJob)
signals.pre_delete.connect(Subscription.pre_delete, sender=Subscription)
signals.pre_save.connect(Subscription.pre_save, sender=Subscription)
signals.post_init.connect(Subscription.post_init, sender=Subscription)
signals.pre_save.connect(Abossignment.pre_save, sender=Abossignment)
