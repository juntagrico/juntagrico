from django.apps import AppConfig

from juntagrico.util import addons


class JuntagricoAppconfig(AppConfig):
    name = "juntagrico_test_addon"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        addons.config.register_admin_menu('addon_test_admin_menu.html')
        addons.config.register_version('juntagrico_test_addon', '0.0.1')
