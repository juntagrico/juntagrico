from django.db import models
from django.contrib.auth.models import User




class Depot(models.Model):
    """
    Location where stuff is picked up.
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"Depot: %s" %(self.name)


class Loco(models.Model):
    """
    Additional fields for Django's default user class.
    """
    user = models.OneToOneField(User, related_name='loco')



