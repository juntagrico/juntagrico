from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.core import validators

import model_audit

class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    weekdays = ((0, "Montag"),
                (1, "Dienstag"),
                (2, "Mittwoch"),
                (3, "cwDonnerstag"),
                (4, "Freitag"),
                (5, "Samstag"),
                (6, "Sonntag"))

    code = models.CharField("Code", max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField("Depot Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    street = models.CharField("Strasse", max_length=100)
    contact = models.ForeignKey(User, on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField("Wochentag", choices=weekdays)


    def __unicode__(self):
        return u"%s" %(self.name)



class AboType(models.Model):
    """
    Represents different types of Abos (subscriptions)
    """
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000)

    # TODO
    #  - frequency: monthly / weekly
    #  - prices: yearly / quarterly / monthly

    def __unicode__(self):
        return u"%s" %(self.name)


class ExtraAboType(models.Model):
    """
    Types of extra abos, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000)


    def __unicode__(self):
        return u"%s" %(self.name)


class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    abotype = models.ForeignKey(AboType, on_delete=models.PROTECT)
    depot = models.ForeignKey(Depot, on_delete=models.PROTECT)
    users = models.ManyToManyField(User, related_name="abos", null=True, blank=True)
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True)

    def __unicode__(self):
        namelist = [self.abotype.name]
        namelist.extend(extra.name for extra in self.extra_abos.all())
        return u"Abo #%s (%s)" %(self.id, " + ".join(namelist))

    def bezieher(self):
        users = self.users.all()
        users = ", ".join(unicode(user) for user in users)
        return users
        

class Anteilschein(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return u"Anteilschein #%s" %(self.id)


class Taetigkeitsbereich(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    coordinator = models.ForeignKey(User, on_delete=models.PROTECT)
    users = models.ManyToManyField(User, related_name="taetigkeitsbereiche")


"""
class Job2Users(models.Model):
    job = models.ForeignKey(Job, on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    slots = models.PositiveIntegerField()


class JobTyp(models.Model):
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    bereich = models.ForeignKey(Taetigkeitsbereich, on_delete=models.PROTECT)


class Job(models.Model):
    typ = models.ForeignKey(JobType, on_delete=models.PROTECT)
    slots = models.PositiveIntegerField("Plaetze")

    #user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    users = models.ManyToManyField(User, through=Job2Users)
"""

# TODO: remove this class? doesn't seem to be needed right now
class Loco(models.Model):
    """
    Additional fields for Django's default user class.
    """
    user = models.OneToOneField(User, related_name='loco')
    # TODO: anteilscheine, taetigkeitsbereiche


    def __unicode__(self):
        return u"%s" %(self.user)


    @classmethod
    def create(cls, sender, instance, created, **kdws):
        """
        Callback to create corresponding loco when new user is created.
        """
        if created:
             new_loco = cls.objects.create(user=instance)


class StaticString(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    text = models.TextField(max_length=10000)

    def __unicode__(self):
        return u"%s" % self.name


model_audit.m2m(Abo.users)
#model_audit.m2m(Abo.extra_abos)

model_audit.fk(Anteilschein.user)

signals.post_save.connect(Loco.create, sender=User)

