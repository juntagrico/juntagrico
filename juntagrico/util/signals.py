import inspect
import sys

from django.db.models import signals

from juntagrico.entity import JuntagricoBaseModel, JuntagricoBasePoly


def set_old_state(sender, instance, **kwds):
    instance._old = instance.__dict__.copy()


def register_entities_for_post_init_and_save():
    model_modules = [key for key in sys.modules if key.startswith('juntagrico.entity.')]
    classes = [item for module_name in model_modules for item in inspect.getmembers(sys.modules[module_name], inspect.isclass)]
    classes = list(dict.fromkeys(classes))
    for name, obj in classes:
        if issubclass(obj, (JuntagricoBaseModel, JuntagricoBasePoly)) and obj != JuntagricoBaseModel and obj != JuntagricoBasePoly:
            signals.post_init.connect(set_old_state, sender=obj)
            signals.post_save.connect(set_old_state, sender=obj)
