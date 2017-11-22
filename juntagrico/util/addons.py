import importlib

from django.core.cache import cache 
from django.conf import settings

def load_config(value,dest,modules):
    for app in modules:
        module=modules[app]
        if hasattr(module, value):
            dest.extend(getattr(module,value)())
    return dest
            
def load_modules():
    modules={}
    for app in settings.INSTALLED_APPS:
        if app.startswith('juntagrico') and app !='juntagrico':
            if importlib.util.find_spec(app + '.juntagricoapp') is not None:
                modules[app] = importlib.import_module(app + '.juntagricoapp')
    return modules

def set_cache(key,value):
    cache.set(key,value)
    
def get_cache(key):
    return  cache.get(key,[])

def set_admin_menus(admin_menus):
    set_cache('admin_menus',admin_menus)

def get_admin_menus():
    return get_cache('admin_menus')
    
    

def get_member_inlines():
    return load_config('member_inlines',[],load_modules())
    
def get_subscription_inlines():
    return load_config('subscription_inlines',[],load_modules())

