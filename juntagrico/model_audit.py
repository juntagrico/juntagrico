from django.db import models
from django.db.models import signals

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Audit(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20)
    field = models.CharField(max_length=100)

    source_type = models.ForeignKey(ContentType, related_name="source_set")
    source_id = models.PositiveIntegerField()
    source_object = GenericForeignKey('source_type', 'source_id')

    target_type = models.ForeignKey(ContentType, related_name="target_set", null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('target_type', 'target_id')


def m2m(m2mrel):
    target_model = m2mrel.field.rel.to
    fieldname = m2mrel.field.name
    # source_ct = ContentType.objects.get_for_model(source_model)
    target_ct = ContentType.objects.get_for_model(target_model)

    def callback(instance, action, pk_set):
        if not action.startswith("post_"):
            return
        action = "m2m" + action[4:]

        if action == "m2m_clear":
            Audit.objects.create(action=action,
                                 field=fieldname,
                                 source_object=instance,
                                 target_type=target_ct)
        elif action in ("m2m_add", "m2m_delete"):
            for obj in target_model.objects.filter(pk__in=pk_set):
                Audit.objects.create(action=action,
                                     field=fieldname,
                                     source_object=instance,
                                     target_object=obj)

    # callback needs to have some reference to it, otherwise set weak=False in the connect call
    signals.m2m_changed.connect(callback, sender=m2mrel.through, weak=False)


def fk(rel):
    source_model = rel.field.model
    target_model = rel.field.rel.to
    fieldname = rel.field.name
    target_ct = ContentType.objects.get_for_model(target_model)

    def callback(instance):
        target_obj = getattr(instance, fieldname)
        kwds = dict(action="fk_set", field=fieldname, source_object=instance)
        # ContentType errors out when passing a target_ct with a null object.
        # Therefore, either pass a non-null object, or just the target_ct
        if target_obj is None:
            kwds["target_type"] = target_ct
        else:
            kwds["target_object"] = target_obj
        Audit.objects.create(**kwds)

    signals.post_save.connect(callback, sender=source_model, weak=False)
