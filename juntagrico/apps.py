import importlib

from django.apps import AppConfig
from django.conf import settings

class JuntagricoAppConfig(AppConfig):
    name = 'juntagrico'

    def ready(self):
        apps = []
        
        admin_menu_templates = []
        
        print('juntagrico searchching for addons:')
        
        for app in settings.INSTALLED_APPS:
            if app.startswith('juntagrico') and app !='juntagrico':
                print('found: ' + app) 
                apps.append(app)
        
        print('searching for admin menus')
        for app in apps:
            if importlib.util.find_spec('admin_menu_template', app + '.juntagricoapp') is not None:
                admin_menu_template.append(app + '.juntagricoapp' + 'admin_menu_template'())