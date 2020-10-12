from django.utils.functional import LazyObject
from django.utils.module_loading import autodiscover_modules


class AddonNotConfigured(Exception):
    pass


class AddonsConfig:

    def __init__(self):
        self._admin_menus = []
        self._admin_subscription_menus = []
        self._user_menus = []
        self._sub_overview = []
        self._sub_change = []
        self._registry = {}
        self._config_classes = []

    def register_admin_menu(self, template):
        self._admin_menus.append(template)

    def get_admin_menus(self):
        return self._admin_menus

    def register_user_menu(self, template):
        self._user_menus.append(template)

    def get_user_menus(self):
        return self._user_menus

    def register_model_inline(self, model, inline):
        inline_list = self._registry.get(model, [])
        inline_list.append(inline)
        self._registry[model] = inline_list

    def register_config_class(self, cls):
        self._config_classes.append(cls)

    def get_model_inlines(self, model):
        return self._registry.get(model, [])

    def register_sub_overview(self, template):
        self._sub_overview.append(template)

    def get_sub_overviews(self):
        return self._sub_overview

    def register_sub_change(self, template):
        self._sub_change.append(template)

    def get_sub_changes(self):
        return self._sub_change

    def register_admin_subscription_menu(self, template):
        self._admin_subscription_menus.append(template)

    def get_admin_subscription_menu(self):
        return self._admin_subscription_menus

    def get_config_classes(self):
        return self._config_classes


class DefaultAddonsConfig(LazyObject):
    def _setup(self):
        self._wrapped = AddonsConfig()


config = DefaultAddonsConfig()


def load_addons():
    autodiscover_modules('juntagricoapp', register_to=config)
