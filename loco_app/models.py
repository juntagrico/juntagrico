from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals

#import model_audit

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
    users = models.ManyToManyField(User, related_name="abos")
    extra_abos = models.ManyToManyField(ExtraAboType, null=True, blank=True)
    # TODO: boehnli, zusatzabos

    def __unicode__(self):
        users = ", ".join(unicode(user) for user in self.current_users())
        if not users:
            users = "niemandem"
    
        namelist = [self.abotype.name]
        namelist.extend(extra.name for extra in self.extra_abos.all())
        return u"#%s %s (von %s)" %(self.id, " + ".join(namelist), users)


    def current_users(self):
        return self.users.all()
        queryset = AboHistory.objects.filter(abo=self, end=None)
        return [ah.user for ah in queryset]
        

#abo_user_log = model_audit.m2m(Abo.users)


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



