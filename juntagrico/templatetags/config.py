from django import template
from juntagrico.config import Config
from juntagrico.util.organisation_name import enriched_organisation as eo

register = template.Library()


@register.simple_tag
def config(property):
    return getattr(Config, property)()


@register.simple_tag
def images(key):
    return Config.images(key)


@register.simple_tag
def vocabulary(key):
    return Config.vocabulary(key)


@register.simple_tag
def enriched_organisation(case):
    return eo(case)
