from django.apps import AppConfig

from juntagrico.util.addons import *


class JuntagricoAppConfig(AppConfig):
    name = 'juntagrico'

    def ready(self):
        modules = load_modules()

        admin_menu_templates = []

        load_config('admin_menu_template', admin_menu_templates, modules)

        set_admin_menus(admin_menu_templates)
