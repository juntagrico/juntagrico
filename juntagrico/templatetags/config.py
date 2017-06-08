from django import template
from juntagrico.config import *

register = template.Library()


@register.simple_tag
def config(property):
    return getattr(Config, property)()
    
@register.simple_tag
def images(key):
    return Config.images(key)
    
