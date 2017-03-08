from django import template
from juntagrico.config import *

register = template.Library()


@register.simple_tag
defconfig(property):
    return getattr(Config,property)()
    
