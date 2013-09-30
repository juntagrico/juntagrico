from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.core import validators
from django.core.exceptions import ValidationError

import model_audit


class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    weekdays = ((0, "Montag"),
                (1, "Dienstag"),
                (2, "Mittwoch"),
                (3, "Donnerstag"),
                (4, "Freitag"),
                (5, "Samstag"),
                (6, "Sonntag"))

    code = models.CharField("Code", max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField("Depot Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    contact = models.ForeignKey(User, on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField("Wochentag", choices=weekdays)

    addr_street = models.CharField("Strasse", max_length=100)
    addr_zipcode = models.CharField("PLZ", max_length=10)
    addr_location = models.CharField("Ort", max_length=50)

    def __unicode__(self):
        return u"%s" %(self.name)


class ExtraAboType(models.Model):
    """
    Types of extra abos, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000)

    def __unicode__(self):
        return u"%s" %(self.name)


class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    depot = models.ForeignKey(Depot, on_delete=models.PROTECT)
    primary_loco = models.ForeignKey("Loco", related_name="abo_primary", null=True, blank=True)
    groesse = models.PositiveIntegerField(default=1)
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True)

    def __unicode__(self):
        namelist = ["1 Einheit" if self.groesse == 1 else "%d Einheiten" % self.groesse]
        namelist.extend(extra.name for extra in self.extra_abos.all())
        return u"Abo (%s)" %(" + ".join(namelist))

    def bezieher(self):
        locos = self.locos.all()
        return ", ".join(unicode(loco) for loco in locos)

    def verantwortlicher_bezieher(self):
        loco = self.primary_loco
        return unicode(loco) if loco is not None else ""


class Anteilschein(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return u"Anteilschein #%s" %(self.id)


class Taetigkeitsbereich(models.Model):
    name = models.CharField("Name", max_length=100, validators=[validators.validate_slug], unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    coordinator = models.ForeignKey(User, on_delete=models.PROTECT)
    users = models.ManyToManyField(User, related_name="taetigkeitsbereiche")

    def __unicode__(self):
        return u'%s' % self.name


class Loco(models.Model):
    """
    Additional fields for Django's default user class.
    """
    user = models.OneToOneField(User, related_name='loco')
    abo = models.ForeignKey(Abo, related_name="locos", null=True, blank=True)

    addr_street = models.CharField("Strasse", max_length=100, null=True, blank=True)
    addr_zipcode = models.CharField("PLZ", max_length=10, null=True, blank=True)
    addr_location = models.CharField("Ort", max_length=50, null=True, blank=True)
    birthday = models.DateField("Geburtsdatum", null=True, blank=True)
    phone = models.CharField("Telefonnr", max_length=50, null=True, blank=True)

    def __unicode__(self):
        return u"%s" %(self.user)

    @classmethod
    def create(cls, sender, instance, created, **kdws):
        """
        Callback to create corresponding loco when new user is created.
        """
        if created:
             cls.objects.create(user=instance)


class JobTyp(models.Model):
    """
    Recurring type of job.
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    bereich = models.ForeignKey(Taetigkeitsbereich, on_delete=models.PROTECT)
    duration = models.PositiveIntegerField("Dauer in Stunden")

    def __unicode__(self):
        return u'%s' % self.name


class Job(models.Model):
    typ = models.ForeignKey(JobTyp, on_delete=models.PROTECT)
    slots = models.PositiveIntegerField("Plaetze")
    time = models.DateTimeField()

    def __unicode__(self):
        return u'Job #%s (%s, %d slots)' % (self.id, self.typ.name, self.slots)



class Boehnli(models.Model):
    """
    Single boehnli (work unit).
    Automatically created during job creation.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    loco = models.ForeignKey(Loco, on_delete=models.PROTECT, null=True, blank=True)
    amount = models.PositiveIntegerField("Anzahl", default=1)

    def __unicode__(self):
        return u'Boehnli #%s' % self.id

    def zeit(self):
        return self.job.time

    @classmethod
    def update(cls, sender, instance, created, **kwds):
        """
        Create and delete boehnli objects as jobs are created and have their amount of slots changed
        """
        if created:
            for i in range(instance.slots):
                cls.objects.create(job=instance)
        else:
            boehnlis = cls.objects.filter(job=instance) 
            current_n = len(boehnlis)
            target_n = instance.slots
            if current_n < target_n:
                for i in range(target_n - current_n):
                    cls.objects.create(job=instance)
            elif current_n > target_n:
                to_delete = current_n - target_n
                free_boehnlis = [boehnli for boehnli in boehnlis if boehnli.loco == None]
                for boehnli in free_boehnlis[:to_delete]:
                    boehnli.delete()
                    


#model_audit.m2m(Abo.users)
model_audit.m2m(Abo.extra_abos)
model_audit.fk(Abo.depot)
model_audit.fk(Anteilschein.user)

signals.post_save.connect(Loco.create, sender=User)
signals.post_save.connect(Boehnli.update, sender=Job)

