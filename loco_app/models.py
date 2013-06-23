from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals

import model_audit

class StaticContent(models.Model):
    """
    All the static contents for the normal webpage
    """
    name = models.CharField("Name", max_length=100)
    content = models.TextField("Html-Inhalt", max_length=10000, default="")


    def __unicode__(self):
        return u"%s" %(self.name)

class Medias(models.Model):
    """
    All the medias that mentioned ortoloco
    """
    mediafile = models.FileField("Datei", upload_to='medias')
    name = models.CharField("Titel", max_length=200)
    year = models.CharField("Jahr", max_length=4)


    def __unicode__(self):
        return u"%s" %(self.name)

class Downloads(models.Model):
    """
    All the downloads available on ortoloco.ch
    """
    mediafile = models.FileField("Datei", upload_to='downloads')
    name = models.CharField("Titel", max_length=200)


    def __unicode__(self):
        return u"%s" %(self.name)

class Links(models.Model):
    """
    All the links that are mentioned on ortoloco.ch
    """
    name = models.CharField("Link", max_length=200)
    description = models.CharField("Beschreibung", max_length=400)

    def __unicode__(self):
        return u"%s" %(self.name)

class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    name = models.CharField("Depot Name", max_length=100)
    description = models.TextField("Beschreibung", max_length=1000, default="")
    street = models.CharField("Strasse", max_length=100)

    # TODO
    #  - responsible_person
    #  - weekday
    #  - enforce lower case constraint at creation time

    def __unicode__(self):
        return u"%s" %(self.name)

    def save(self, *args, **kwds):
        """
        Override django method to force name to be lowercase.
        """
        self.name = self.name.lower()
        models.Model.save(self, *args, **kwds)



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
    abotype = models.ForeignKey(AboType)
    depot = models.ForeignKey(Depot)
    users = models.ManyToManyField(User, related_name="abos", null=True, blank=True)
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True)
    # TODO: boehnli, zusatzabos

    def __unicode__(self):
        namelist = [self.abotype.name]
        namelist.extend(extra.name for extra in self.extra_abos.all())
        return u"Abo #%s (%s)" %(self.id, " + ".join(namelist))


    def bezieher(self):
        users = self.users.all()
        users = ", ".join(unicode(user) for user in users)
        return users
        

abo_user_audit = model_audit.m2m(Abo.users)
extraabo_audit = model_audit.m2m(Abo.extra_abos)


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


signals.post_save.connect(Loco.create, sender=User)


class StaticString(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    text = models.TextField(max_length=10000)


