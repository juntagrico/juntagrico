from django.db import models
from django.db.models import signals



def m2m(m2mrel):
    source_model = m2mrel.field.model
    target_model = m2mrel.field.rel.to
    cls = m2mrel.through

    class Meta:
        db_table = "%s_audit" % cls._meta.db_table
        app_label = cls._meta.app_label
        verbose_name_plural = '%s audit trail' % cls._meta.verbose_name

    attrs = {
        '__module__': cls.__module__,
        'Meta': Meta,
        'timestamp': models.DateTimeField(auto_now_add=True),
        'action': models.CharField(max_length=20, default=""),
        'fm': models.ForeignKey(source_model, null=True, blank=True),
        'to': models.ForeignKey(target_model, null=True, blank=True),
        }

    audit_cls = type("%s_audit" % cls.__name__, (models.Model,), attrs)

    def callback(instance, action, pk_set, **kwds):
        if not action.startswith("post_"):
            return
        action = action[5:]

        if action == "clear":
            audit_cls.objects.create(action=action, fm=instance)
        elif action in ("add", "delete"):
            for obj in target_model.objects.filter(pk__in=pk_set):
                audit_cls.objects.create(action=action, fm=instance, to=obj)

    # callback needs to have some reference to it, otherwise set weak=False in the connect call
    signals.m2m_changed.connect(callback, sender=cls, weak=False)
    return audit_cls



