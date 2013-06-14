from django.db import models
from django.db.models import signals



def m2m(m2mrel):
    source_model = m2mrel.field.model
    target_model = m2mrel.field.rel.to

    class Log(models.Model):
        fm = models.ForeignKey(source_model, null=True, blank=True)
        to = models.ForeignKey(target_model, null=True, blank=True)
        action = models.CharField(max_length=20, default="")

        def __unicode__(self):
            return u"%s %s log instance" %(source_model, target_model)

        @classmethod
        def callback(cls, instance, action, **kwds):
            # stub
            log = cls.objects.create(fm=instance, action=action)


    Log.__name__ = "%s %s" %(m2mrel.field.m2m_field_name(), m2mrel.field.m2m_reverse_field_name())

    # Log needs to be in models.py namespace
    # callback needs to have some reference to it, otherwise set weakref=False in the connect call
    signals.m2m_changed.connect(Log.callback, sender=m2mrel.through)
    return Log



