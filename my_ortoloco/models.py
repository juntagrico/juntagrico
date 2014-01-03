# encoding: utf-8

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.core import validators
from django.core.exceptions import ValidationError
import time

import model_audit
import helpers


class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    code = models.CharField("Code", max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField("Depot Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    contact = models.ForeignKey("Loco", on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField("Wochentag", choices=helpers.weekday_choices)
    latitude = models.CharField("Latitude", max_length=100, default="")
    longitude = models.CharField("Longitude", max_length=100, default="")

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    def wochentag(self):
        day = "Unbekannt"
        if self.weekday < 8 and self.weekday > 0:
            day = helpers.weekdays[self.weekday]
        return day

    def small_abos(self):
        return len(self.abo_set.all().filter(groesse=1))

    def big_abos(self):
        return len(self.abo_set.all().filter(groesse=2))

    def vier_eier(self):
        eier = 0
        for abo in self.abo_set.all():
            eier += len(abo.extra_abos.all().filter(description="Eier 4er Pack"))
        return eier

    def sechs_eier(self):
        eier = 0
        for abo in self.abo_set.all():
            eier += len(abo.extra_abos.all().filter(description="Eier 6er Pack"))
        return eier

    def kaese_ganz(self):
        kaese = 0
        for abo in self.abo_set.all():
            kaese += len(abo.extra_abos.all().filter(description="Käse ganz"))
        return kaese

    def kaese_halb(self):
        kaese = 0
        for abo in self.abo_set.all():
            kaese += len(abo.extra_abos.all().filter(description="Käse halb"))
        return kaese

    def kaese_viertel(self):
        kaese = 0
        for abo in self.abo_set.all():
            kaese += len(abo.extra_abos.all().filter(description="Käse viertel"))
        return kaese

    def big_obst(self):
        obst = 0
        for abo in self.abo_set.all():
            obst += len(abo.extra_abos.all().filter(description="Obst gr. (2kg)"))
        return obst

    def small_obst(self):
        obst = 0
        for abo in self.abo_set.all():
            obst += len(abo.extra_abos.all().filter(description="Obst kl. (1kg)"))
        return obst

    class Meta:
        verbose_name = "Depot"
        verbose_name_plural = "Depots"


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
    groesse = models.PositiveIntegerField(default=1)
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True)
    primary_loco = models.ForeignKey("Loco", related_name="abo_primary", null=True, blank=True,
                                     on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        namelist = ["1 Einheit" if self.groesse == 1 else "%d Einheiten" % self.groesse]
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

    def verantwortlicher_bezieher(self):
        loco = self.primary_loco
        return unicode(loco) if loco is not None else ""

    def haus_abos(self):
        return int(self.groesse / 10)

    def grosse_abos(self):
        return int((self.groesse % 10) / 2)

    def kleine_abos(self):
        return self.groesse % 2

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
    user = models.OneToOneField(User, related_name='loco')

    first_name = models.CharField("Vorname", max_length=30)
    last_name = models.CharField("Nachname", max_length=30)
    email = models.EmailField()

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)
    birthday = models.DateField("Geburtsdatum", null=True, blank=True)
    phone = models.CharField("Telefonnr", max_length=50)
    mobile_phone = models.CharField("Mobile", max_length=50, null=True, blank=True)

    abo = models.ForeignKey(Abo, related_name="locos", null=True, blank=True,
                            on_delete=models.SET_NULL)


    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    @classmethod
    def create(cls, sender, instance, created, **kdws):
        """
        Callback to create corresponding loco when new user is created.
        """
        if created:
            cls.objects.create(user=instance)

    class Meta:
        verbose_name = "Loco"
        verbose_name_plural = "Locos"


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


class JobTyp(models.Model):
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
    typ = models.ForeignKey(JobTyp, on_delete=models.PROTECT)
    slots = models.PositiveIntegerField("Plaetze")
    time = models.DateTimeField()

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
        participants = boehnlis.count()
        pctfull = participants * 100 / self.slots
        if pctfull >= 100:
            return "erbse_voll.png"
        elif pctfull >= 75:
            return "erbse_fast_voll.png"
        elif pctfull >= 50:
            return "erbse_halb.png"
        else:
            return "erbse_fast_leer.png"

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

    class Meta:
        verbose_name = 'Böhnli'
        verbose_name_plural = 'Böhnlis'


#model_audit.m2m(Abo.users)
model_audit.m2m(Abo.extra_abos)
model_audit.fk(Abo.depot)
model_audit.fk(Anteilschein.loco)

signals.post_save.connect(Loco.create, sender=User)

