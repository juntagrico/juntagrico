import importlib
from importlib import util

from django.core.cache import cache
from django.conf import settings


def load_config(value, dest, modules):
    for app in modules:
        module = modules[app]
        if hasattr(module, value):
            dest.extend(getattr(module, value)())
    return dest


def load_modules():
    modules = {}
    for app in settings.INSTALLED_APPS:
        j_app = app.startswith('juntagrico') and app != 'juntagrico'
        if j_app and util.find_spec(app + '.juntagricoapp') is not None:
            modules[app] = importlib.import_module(app + '.juntagricoapp')
    return modules


def set_cache(key, value):
    cache.set(key, value)


def get_cache(key):
    return cache.get(key, [])


def set_admin_menus(admin_menus):
    set_cache('admin_menus', admin_menus)


def get_admin_menus():
    return get_cache('admin_menus')


def get_member_inlines():
    return load_config('member_inlines', [], load_modules())


def get_job_inlines():
    return load_config('job_inlines', [], load_modules())


def get_jobextra_inlines():
    return load_config('jobextra_inlines', [], load_modules())


def get_jobextratype_inlines():
    return load_config('jobextratype_inlines', [], load_modules())


def get_subsize_inlines():
    return load_config('subsize_inlines', [], load_modules())


def get_subtype_inlines():
    return load_config('subtype_inlines', [], load_modules())


def get_area_inlines():
    return load_config('area_inlines', [], load_modules())


def get_assignment_inlines():
    return load_config('assignment_inlines', [], load_modules())


def get_share_inlines():
    return load_config('share_inlines', [], load_modules())


def get_depot_inlines():
    return load_config('depot_inlines', [], load_modules())


def get_extrasub_inlines():
    return load_config('extrasub_inlines', [], load_modules())


def get_extrasubcat_inlines():
    return load_config('extrasubcat_inlines', [], load_modules())


def get_extrasubtype_inlines():
    return load_config('extrasubtype_inlines', [], load_modules())


def get_delivery_inlines():
    return load_config('delivery_inlines', [], load_modules())


def get_jobtype_inlines():
    return load_config('jobtype_inlines', [], load_modules())


def get_otjob_inlines():
    return load_config('otjob_inlines', [], load_modules())


def get_subscription_inlines():
    return load_config('subscription_inlines', [], load_modules())
