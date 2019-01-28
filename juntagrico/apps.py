from django.apps import AppConfig

from juntagrico.util.addons import *


class JuntagricoAppConfig(AppConfig):
    name = 'juntagrico'

    def ready(self):
        modules = load_modules()
        admin_menu_templates = []
        menu_templates = []
        load_config('admin_menu_template', admin_menu_templates, modules)
        load_config('menu_template', menu_templates, modules)
        set_admin_menus(admin_menu_templates)
        set_user_menus(menu_templates)
