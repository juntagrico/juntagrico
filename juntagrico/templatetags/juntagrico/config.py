from django import template

from juntagrico.config import Config
from juntagrico.util.addons import config as addons_config
from juntagrico.util.organisation_name import enriched_organisation as eo

register = template.Library()


@register.simple_tag
def config(property):
    for config in get_config_classes():
        if hasattr(config, property):
            return getattr(config, property)()


@register.simple_tag
def images(key):
    return Config.images(key)


@register.simple_tag
def vocabulary(key):
    return Config.vocabulary(key)


@register.simple_tag
def enriched_organisation(case):
    return eo(case)


@register.simple_tag
def cookie_consent(key):
    return Config.cookie_consent(key)


def get_config_classes():
    configs = [Config]
    configs.extend(addons_config.get_config_classes())
    return configs
