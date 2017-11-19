from django.apps import AppConfig
from django.conf import settings

class JuntagricoAppConfig(AppConfig):
    name = 'juntagrico'

    def ready(self):
        print('juntagrico searchching for addons:')
        
        for app in settings.INSTALLED_APPS:
            if app.startswith('juntagrico') and app !='juntagrico':
                print('found: ' + app) 