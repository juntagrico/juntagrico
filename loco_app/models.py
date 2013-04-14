from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save



class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    name = models.CharField("Depot Name", max_length=100)
    description = models.CharField("Beschreibung", max_length=10000, default="")
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
    Represents all different types of Abos (subscriptions), e.g. veggies (small / large bag), eggs, cheese.
    """
    name = models.CharField("Name", max_length=100)
    description = models.CharField("Beschreibung", max_length=10000)

    # TODO
    #  - frequency: monthly / weekly
    #  - prices: yearly / quarterly / monthly


    def __unicode__(self):
        return u"%s" %(self.name)



class Abo(models.Model):
    """
    One Abo that may be shared among several people.
    """
    abotype = models.ForeignKey(AboType)
    depot = models.ForeignKey(Depot)

    def __unicode__(self):
        users = ", ".join(unicode(loco.user) for loco in self.locos.all())
        if not users:
            users = "niemandem"

        return u"%s (von %s)" %(self.abotype.name, users)


    
class Loco(models.Model):
    """
    Additional fields for Django's default user class.
    """
    user = models.OneToOneField(User, related_name='loco')
    abos = models.ManyToManyField(Abo, related_name='locos', blank=True, null=True)

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


