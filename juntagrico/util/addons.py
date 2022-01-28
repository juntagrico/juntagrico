from django.utils.functional import LazyObject
from django.utils.module_loading import autodiscover_modules


class AddonNotConfigured(Exception):
    pass


class TemplateHookRegistry:
    def __init__(self):
        self._hooks = {}

    def register(self, hook, templates=None):
        """ registers hook (with default templates)
        """
        self._hooks[hook] = templates or []

    def insert_at(self, hook, pos, template):
        if template in self._hooks[hook]:
            del self._hooks[hook][template]  # replace if it was already in the list
        self._hooks[hook].insert(pos, template)

    def append(self, hook, template):
        self.insert_at(hook, len(self._hooks[hook]), template)

    def prepend(self, hook, template):
        self.insert_at(hook, 0, template)

    def inser_after(self, hook, after, template):
        self.insert_at(hook, self._hooks[hook].index(after) + 1, template)

    def insert_before(self, hook, before, template):
        self.insert_at(hook, self._hooks[hook].index(before), template)

    def get(self, hook):
        return self._hooks[hook]


class AddonsConfig:

    def __init__(self):
        self._admin_menus = []
        self._admin_subscription_menus = []
        self._show_admin_menu_methods = []
        self._user_menus = []
        self._sub_overview = []
        self._sub_change = []
        self._registry = {}
        self._config_classes = []
        self._versions = {}
        self.template = TemplateHookRegistry()

    def register_admin_menu(self, template):
        self._admin_menus.append(template)

    def get_admin_menus(self):
        return self._admin_menus

    def register_show_admin_menu_method(self, method):
        self._show_admin_menu_methods.append(method)

    def show_admin_menu(self, user):
        result = False
        for method in self._show_admin_menu_methods:
            result = result or method(user)
        return result

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

    def register_version(self, name, version):
        self._versions[name] = version

    def get_versions(self):
        return self._versions


class DefaultAddonsConfig(LazyObject):
    def _setup(self):
        self._wrapped = AddonsConfig()


config = DefaultAddonsConfig()


def load_addons():
    autodiscover_modules('juntagricoapp', register_to=config)
