from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save



class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    name = models.CharField("Depot Name", max_length=100)
    description = models.CharField("Beschreibung", max_length=1000, default="")
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
    description = models.CharField("Beschreibung", max_length=1000)

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
    description = models.CharField("Beschreibung", max_length=1000)


    def __unicode__(self):
        return u"%s" %(self.name)


class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    abotype = models.ForeignKey(AboType)
    depot = models.ForeignKey(Depot)
    user_history = models.ManyToManyField(User, related_name="abo_history", through="AboHistory") 
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
        queryset = AboHistory.objects.filter(abo=self, end=None)
        return [ah.user for ah in queryset]
        


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


post_save.connect(Loco.create, sender=User)


class AboHistory(models.Model):
    """
    Defines the User-Abo manytomany relation.

    This is a complete history of abo memberships. currently active abos are found by filtering
    for end=None
    """
    abo = models.ForeignKey(Abo)
    user = models.ForeignKey(User)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

    def __unicode__(self):
        if self.end is None:
            return u"%s von %s" % (self.user, self.start)
        return u"%s von %s bis %s" % (self.user, self.start, self.end)

