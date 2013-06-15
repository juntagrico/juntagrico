from django.db import models
from django.db.models import signals

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Audit(models.Model):
    source_type = models.ForeignKey(ContentType, related_name="source_set")
    source_id = models.PositiveIntegerField()
    source_object = generic.GenericForeignKey('source_type', 'source_id')

    target_type = models.ForeignKey(ContentType, related_name="target_set", null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = generic.GenericForeignKey('target_type', 'target_id')

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, default="")


def m2m(m2mrel):
    source_model = m2mrel.field.model
    target_model = m2mrel.field.rel.to

    #source_ct = ContentType.objects.get_for_model(source_model)
    target_ct = ContentType.objects.get_for_model(target_model)

    def callback(instance, action, pk_set, **kwds):
        if not action.startswith("post_"):
            return
        action = action[5:]

        if action == "clear":
            Audit.objects.create(action=action, source_object=instance, target_type=target_ct)
        elif action in ("add", "delete"):
            for obj in target_model.objects.filter(pk__in=pk_set):
                Audit.objects.create(action=action, source_object=instance, target_object=obj)

    # callback needs to have some reference to it, otherwise set weak=False in the connect call
    signals.m2m_changed.connect(callback, sender=m2mrel.through, weak=False)

