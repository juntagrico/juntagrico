from django import template

register = template.Library()


@register.filter
def extra_abo(abo, code):
    return abo.extra_abo(code)
    
