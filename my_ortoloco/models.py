# encoding: utf-8

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.core import validators
import time
from django.db.models import Q

import model_audit
import helpers


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

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)


    def active_abos(self):
        return self.abo_set.filter(active=True)

    def wochentag(self):
        day = "Unbekannt"
        if self.weekday < 8 and self.weekday > 0:
            day = helpers.weekdays[self.weekday]
        return day

    def small_abos(self):
        return len(self.active_abos().filter(Q(size=1) | Q(size=3)))

    def big_abos(self):
        return len(self.active_abos().filter(Q(size=2) | Q(size=3) | Q(size=4))) + len(self.active_abos().filter(size=4))

    def vier_eier(self):
        eier = 0
        for abo in self.active_abos().all():
            eier += len(abo.extra_abos.all().filter(description="Eier 4er Pack"))
        return eier

    def sechs_eier(self):
        eier = 0
        for abo in self.active_abos().all():
            eier += len(abo.extra_abos.all().filter(description="Eier 6er Pack"))
        return eier

    def kaese_ganz(self):
        kaese = 0
        for abo in self.active_abos().all():
            kaese += len(abo.extra_abos.all().filter(description="Käse ganz"))
        return kaese

    def kaese_halb(self):
        kaese = 0
        for abo in self.active_abos().all():
            kaese += len(abo.extra_abos.all().filter(description="Käse halb"))
        return kaese

    def kaese_viertel(self):
        kaese = 0
        for abo in self.active_abos().all():
            kaese += len(abo.extra_abos.all().filter(description="Käse viertel"))
        return kaese

    def big_obst(self):
        obst = 0
        for abo in self.active_abos().all():
            obst += len(abo.extra_abos.all().filter(description="Obst gr. (2kg)"))
        return obst

    def small_obst(self):
        obst = 0
        for abo in self.active_abos().all():
            obst += len(abo.extra_abos.all().filter(description="Obst kl. (1kg)"))
        return obst

    class Meta:
        verbose_name = "Depot"
        verbose_name_plural = "Depots"
        permissions = (('is_depot_admin', 'Benutzer ist Depot Admin'),)


class ExtraAboType(models.Model):
    """
    Types of extra abos, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo"
        verbose_name_plural = "Zusatz-Abos"


class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    depot = models.ForeignKey(Depot, on_delete=models.PROTECT)
    size = models.PositiveIntegerField(default=1)
    future_size = models.PositiveIntegerField("Zukuenftige Groesse", default=1)
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True, related_name="extra_abos")
    extra_abos_changed = models.BooleanField(default=False)
    future_extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True, related_name="future_extra_abos")
    primary_loco = models.ForeignKey("Loco", related_name="abo_primary", null=True, blank=True,
                                     on_delete=models.PROTECT)
    active = models.BooleanField(default=False)

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

    def size_name(self):
        return Abo.get_size_name(size=self.size)

    def future_size_name(self):
        return Abo.get_size_name(size=self.future_size)

    def vier_eier(self):
        return len(self.extra_abos.all().filter(description="Eier 4er Pack")) > 0

    def sechs_eier(self):
        return len(self.extra_abos.all().filter(description="Eier 6er Pack")) > 0

    def ganze_kaese(self):
        return len(self.extra_abos.all().filter(description="Käse ganz")) > 0

    def halbe_kaese(self):
        return len(self.extra_abos.all().filter(description="Käse halb")) > 0

    def viertel_kaese(self):
        return len(self.extra_abos.all().filter(description="Käse viertel")) > 0

    def gross_obst(self):
        return len(self.extra_abos.all().filter(description="Obst gr. (2kg)")) > 0

    def klein_obst(self):
        return len(self.extra_abos.all().filter(description="Obst kl. (1kg)")) > 0

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

    def __unicode__(self):
        return u"Anteilschein #%s" % (self.id)

    class Meta:
        verbose_name = "Anteilschein"
        verbose_name_plural = "Anteilscheine"


class Taetigkeitsbereich(models.Model):
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    core = models.BooleanField("Kernbereich", default=False)
    hidden = models.BooleanField("versteckt", default=False)
    coordinator = models.ForeignKey(Loco, on_delete=models.PROTECT)
    locos = models.ManyToManyField(Loco, related_name="areas", blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = 'Tätigkeitsbereich'
        verbose_name_plural = 'Tätigkeitsbereiche'


class JobType(models.Model):
    """
    Recurring type of job.
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
        verbose_name = 'Jobart'
        verbose_name_plural = 'Jobarten'


class Job(models.Model):
    typ = models.ForeignKey(JobType, on_delete=models.PROTECT)
    slots = models.PositiveIntegerField("Plaetze")
    time = models.DateTimeField()
    pinned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField("Reminder verschickt", default=False)

    def __unicode__(self):
        return u'Job #%s' % (self.id)


    def wochentag(self):
        weekday = helpers.weekdays[self.time.isoweekday()]
        return weekday[:2]

    def time_stamp(self):
        return int(time.mktime(self.time.timetuple()) * 1000)

    def freie_plaetze(self):
        return self.slots - self.besetzte_plaetze()

    def end_time(self):
        return self.time + datetime.timedelta(hours=self.typ.duration)

    def besetzte_plaetze(self):
        return self.boehnli_set.count()

    def get_status_bohne(self):
        boehnlis = Boehnli.objects.filter(job_id=self.id)
        return helpers.get_status_bean(boehnlis.count() * 100 / self.slots)

    def is_in_kernbereich(self):
        return self.typ.bereich.core

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'


class Boehnli(models.Model):
    """
    Single boehnli (work unit).
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    loco = models.ForeignKey(Loco, on_delete=models.PROTECT)

    def __unicode__(self):
        return u'Boehnli #%s' % self.id

    def zeit(self):
        return self.job.time

    def is_in_kernbereich(self):
        return self.job.typ.bereich.core

    class Meta:
        verbose_name = 'Böhnli'
        verbose_name_plural = 'Böhnlis'


#model_audit.m2m(Abo.users)
model_audit.m2m(Abo.extra_abos)
model_audit.fk(Abo.depot)
model_audit.fk(Anteilschein.loco)

signals.post_save.connect(Loco.create, sender=Loco)
signals.post_delete.connect(Loco.post_delete, sender=Loco)

