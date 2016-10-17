# encoding: utf-8

import datetime
import time

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.utils import timezone
from polymorphic.models import PolymorphicModel

import helpers
import model_audit
from my_ortoloco.mailer import *


class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    code = models.CharField("Code", max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField("Depot Name", max_length=100, unique=True)
    contact = models.ForeignKey("Loco", on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField("Wochentag", choices=helpers.weekday_choices)
    latitude = models.CharField("Latitude", max_length=100, default="")
    longitude = models.CharField("Longitude", max_length=100, default="")

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)

    description = models.TextField("Beschreibung", max_length=1000, default="")

    overview_cache = None
    abo_cache = None

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    def active_abos(self):
        return self.abo_set.filter(active=True)

    @property
    def wochentag(self):
        day = "Unbekannt"
        if 8 > self.weekday > 0:
            day = helpers.weekdays[self.weekday]
        return day

    @property
    def small_abos_t(self):
        return self.small_abos(self.active_abos())

    @staticmethod
    def small_abos(abos):
        return len(abos.filter(Q(size=1) | Q(size=3)))

    def big_abos_t(self):
        return self.big_abos(self.active_abos())

    def big_abos(self, abos):
        return len(abos.filter(Q(size=2) | Q(size=3) | Q(size=4))) + len(
            self.active_abos().filter(size=4))

    @staticmethod
    def extra_abo(abos, code):
        amount = 0
        for abo in abos.all():
            amount += len(abo.extra_abos.all().filter(name=code))
        return amount

    def fill_overview_cache(self):
        self.fill_active_abo_cache()
        self.overview_cache = []
        self.overview_cache.append(int(self.small_abos(self.abo_cache)))
        self.overview_cache.append(self.big_abos(self.abo_cache))
        for category in ExtraAboCategory.objects.all().order_by("sort_order"):
            for extra_abo in ExtraAboType.objects.all().filter(category=category).order_by("sort_order"):
                code = extra_abo.name
                self.overview_cache.append(self.extra_abo(self.abo_cache, code))

    def fill_active_abo_cache(self):
        self.abo_cache = self.active_abos()

    class Meta:
        verbose_name = "Depot"
        verbose_name_plural = "Depots"
        permissions = (('is_depot_admin', 'Benutzer ist Depot Admin'),)


class ExtraAboType(models.Model):
    """
    Types of extra abos, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    size = models.CharField("Groesse (gross,4, ...)", max_length=100, default="")
    description = models.TextField("Beschreibung", max_length=1000)
    sort_order = models.FloatField("Groesse zum Sortieren", default=1.0)
    category = models.ForeignKey("ExtraAboCategory", related_name="category", null=True, blank=True,
                                 on_delete=models.PROTECT)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo"
        verbose_name_plural = "Zusatz-Abos"


class ExtraAboCategory(models.Model):
    """
    Types of extra abos, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, blank=True)
    sort_order = models.FloatField("Nummer zum Sortieren", default=1.0)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo-Kategorie"
        verbose_name_plural = "Zusatz-Abo-Kategorien"


class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name="abo_set")
    future_depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name="future_abo_set", null=True,
                                     blank=True, )
    size = models.PositiveIntegerField(default=1)
    future_size = models.PositiveIntegerField("Zukuenftige Groesse", default=1)
    extra_abos = models.ManyToManyField(ExtraAboType, blank=True, related_name="extra_abos")
    extra_abos_changed = models.BooleanField(default=False)
    future_extra_abos = models.ManyToManyField(ExtraAboType, blank=True, related_name="future_extra_abos")
    primary_loco = models.ForeignKey("Loco", related_name="abo_primary", null=True, blank=True,
                                     on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    activation_date = models.DateField("Aktivierungssdatum", null=True, blank=True)
    deactivation_date = models.DateField("Deaktivierungssdatum", null=True, blank=True)
    old_active = None

    def __unicode__(self):
        namelist = ["1 Einheit" if self.size == 1 else "%d Einheiten" % self.size]
        namelist.extend(extra.name for extra in self.extra_abos.all())
        return u"Abo (%s) %s" % (" + ".join(namelist), self.id)

    def bezieher(self):
        locos = self.locos.all()
        return ", ".join(unicode(loco) for loco in locos)

    def andere_bezieher(self):
        locos = self.bezieher_locos().exclude(email=self.primary_loco.email)
        return ", ".join(unicode(loco) for loco in locos)

    def bezieher_locos(self):
        return self.locos.all()

    def primary_loco_nullsave(self):
        loco = self.primary_loco
        return unicode(loco) if loco is not None else ""

    def small_abos(self):
        return self.size % 2

    def big_abos(self):
        return int((self.size % 10) / 2)

    def house_abos(self):
        return int(self.size / 10)

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
            return "Kleines Abo"
        elif size == 2:
            return "Grosses Abo"
        elif size == 10:
            return "Haus Abo"
        elif size == 3:
            return "Kleines + Grosses Abo"
        elif size == 4:
            return "2 Grosse Abos"
        else:
            return "Kein Abo"

    @property
    def size_name(self):
        return Abo.get_size_name(size=self.size)

    @property
    def future_size_name(self):
        return Abo.get_size_name(size=self.future_size)

    def extra_abo(self, code):
        return len(self.extra_abos.all().filter(name=code)) > 0

    def clean(self):
        if self.old_active != self.active and self.deactivation_date is not None:
            raise ValidationError(u'Deaktivierte Abos koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active == False and instance.deactivation_date is None:
            instance.activation_date = timezone.now().date()
        elif instance.old_active != instance.active and instance.old_active == True and instance.deactivation_date is None:
            instance.deactivation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active

    @classmethod
    def pre_delete(cls, sender, instance, **kwds):
        for loco in instance.bezieher_locos():
            loco.abo = None
            loco.save()

    class Meta:
        verbose_name = "Abo"
        verbose_name_plural = "Abos"


class Loco(models.Model):
    """
    Additional fields for Django's default user class.
    """

    # user class is only used for logins, permissions, and other builtin django stuff
    # all user information should be stored in the Loco model
    user = models.OneToOneField(User, related_name='loco', null=True, blank=True)

    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)
    birthday = models.DateField("Geburtsdatum", null=True, blank=True)
    boehnlis = models.PositiveSmallIntegerField("Boehnlis", default=0)
    phone = models.CharField("Telefonnr", max_length=50)
    mobile_phone = models.CharField("Mobile", max_length=50, null=True, blank=True)

    abo = models.ForeignKey(Abo, related_name="locos", null=True, blank=True,
                            on_delete=models.SET_NULL)

    confirmed = models.BooleanField("bestätigt", default=True)
    reachable_by_email = models.BooleanField("Kontaktierbar von der Job Seite aus", default=False)
    block_emails = models.BooleanField("keine emails", default=False)

    old_abo = None

    def __unicode__(self):
        return self.get_name()

    @classmethod
    def create(cls, sender, instance, created, **kdws):
        """
        Callback to create corresponding loco when new user is created.
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
        if instance.old_abo != instance.abo and instance.abo is None:
            instance.areas = ()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_abo = instance.abo

    class Meta:
        verbose_name = "Loco"
        verbose_name_plural = "Locos"

    def get_name(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def get_phone(self):
        if self.mobile_phone != "":
            return self.mobile_phone
        return self.phone


class Anteilschein(models.Model):
    loco = models.ForeignKey(Loco, null=True, blank=True, on_delete=models.SET_NULL)
    paid = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    paid_date = models.DateField("Bezahlt am", null=True, blank=True)
    canceled_date = models.DateField("Canceled am", null=True, blank=True)
    number = models.IntegerField("Anteilschein Nummer", null=True, blank=True)
    notes = models.TextField("Notizen", max_length=1000, default="", blank=True)

    def __unicode__(self):
        return u"Anteilschein #%s" % self.id

    class Meta:
        verbose_name = "Anteilschein"
        verbose_name_plural = "Anteilscheine"


class Taetigkeitsbereich(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    core = models.BooleanField("Kernbereich", default=False)
    hidden = models.BooleanField("versteckt", default=False)
    coordinator = models.ForeignKey(Loco, on_delete=models.PROTECT)
    locos = models.ManyToManyField(Loco, related_name="areas", blank=True)
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


class AbstractJobType(models.Model):
    """
    Abstract type of job.
    """
    name = models.CharField("Name", max_length=100, unique=True)
    displayed_name = models.CharField("Angezeigter Name", max_length=100, blank=True, null=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    bereich = models.ForeignKey(Taetigkeitsbereich, on_delete=models.PROTECT)
    duration = models.PositiveIntegerField("Dauer in Stunden")
    location = models.CharField("Ort", max_length=100, default="")

    def __unicode__(self):
        return u'%s - %s' % (self.bereich, self.get_name())

    def get_name(self):
        if self.displayed_name is not None:
            return self.displayed_name
        return self.name

    class Meta:
        verbose_name = 'AbstractJobart'
        verbose_name_plural = 'AbstractJobarten'
        abstract = True


class JobType(AbstractJobType):
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
    def typ(self):
        raise NotImplementedError

    def __unicode__(self):
        return u'Job #%s' % self.id

    def wochentag(self):
        weekday = helpers.weekdays[self.time.isoweekday()]
        return weekday[:2]

    def time_stamp(self):
        return int(time.mktime(self.time.timetuple()) * 1000)

    def freie_plaetze(self):
        if not (self.slots is None):
            return self.slots - self.besetzte_plaetze()
        else:
            return 0

    def end_time(self):
        return self.time + datetime.timedelta(hours=self.typ.duration)

    def start_time(self):
        return self.time

    def besetzte_plaetze(self):
        return self.boehnli_set.count()

    def get_status_bohne(self):
        boehnlis = Boehnli.objects.filter(job_id=self.id)
        if self.slots < 1:
            return helpers.get_status_bean(100)
        return helpers.get_status_bean(boehnlis.count() * 100 / self.slots)

    def is_in_kernbereich(self):
        return self.typ.bereich.core

    def clean(self):
        if self.old_canceled != self.canceled and self.old_canceled == True:
            raise ValidationError(u'Abgesagte jobs koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_canceled != instance.canceled and instance.old_canceled == False:
            boehnlis = Boehnli.objects.filter(job_id=instance.id)
            emails = set()
            for boehnli in boehnlis:
                emails.add(boehnli.loco.email)
            instance.slots = 0
            if len(emails) > 0:
                send_job_canceled(emails, instance, "www.ortoloco.ch")
        if instance.old_time != instance.time:
            boehnlis = Boehnli.objects.filter(job_id=instance.id)
            emails = set()
            for boehnli in boehnlis:
                emails.add(boehnli.loco.email)
            if len(emails) > 0:
                send_job_time_changed(emails, instance, "www.ortoloco.ch")

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_time = instance.time
        instance.old_canceled = instance.canceled
        if instance.canceled:
            boehnlis = Boehnli.objects.filter(job_id=instance.id)
            boehnlis.delete()

    class Meta:
        verbose_name = 'AbstractJob'
        verbose_name_plural = 'AbstractJobs'


class RecuringJob(Job):
    typ = models.ForeignKey(JobType, on_delete=models.PROTECT)

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'


class OneTimeJob(Job, AbstractJobType):
    """
    One time job. Do not add Field here do it in the Parent class
    """

    @property
    def typ(self):
        return self

    def __unicode__(self):
        return u'%s - %s' % (self.bereich, self.get_name())

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = 'EinzelJob'
        verbose_name_plural = 'EinzelJobs'


class Boehnli(models.Model):
    """
    Single boehnli (work unit).
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    loco = models.ForeignKey(Loco, on_delete=models.PROTECT)
    core_cache = models.BooleanField("Kernbereich", default=False)

    def __unicode__(self):
        return u'Boehnli #%s' % self.id

    def zeit(self):
        return self.job.time

    def is_in_kernbereich(self):
        return self.job.typ.bereich.core

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        instance.core_cache = instance.is_in_kernbereich()

    class Meta:
        verbose_name = 'Böhnli'
        verbose_name_plural = 'Böhnlis'


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
                       ('is_book_keeper', 'Benutzer ist Buchhalter'),)


# model_audit.m2m(Abo.users)
model_audit.m2m(Abo.extra_abos)
model_audit.fk(Abo.depot)
model_audit.fk(Anteilschein.loco)

signals.post_save.connect(Loco.create, sender=Loco)
signals.post_delete.connect(Loco.post_delete, sender=Loco)
signals.pre_save.connect(Loco.pre_save, sender=Loco)
signals.post_init.connect(Loco.post_init, sender=Loco)
signals.pre_save.connect(Job.pre_save, sender=Job)
signals.post_init.connect(Job.post_init, sender=Job)
signals.pre_save.connect(RecuringJob.pre_save, sender=RecuringJob)
signals.post_init.connect(RecuringJob.post_init, sender=RecuringJob)
signals.pre_save.connect(OneTimeJob.pre_save, sender=OneTimeJob)
signals.post_init.connect(OneTimeJob.post_init, sender=OneTimeJob)
signals.pre_delete.connect(Abo.pre_delete, sender=Abo)
signals.pre_save.connect(Abo.pre_save, sender=Abo)
signals.post_init.connect(Abo.post_init, sender=Abo)
signals.pre_save.connect(Boehnli.pre_save, sender=Boehnli)
