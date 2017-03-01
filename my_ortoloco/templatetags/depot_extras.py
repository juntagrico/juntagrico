from django import template

register = template.Library()


@register.filter
def abos_amount(abo, name):
    return abo.abo_amount(name)
    
@register.filter
def extra_abo(abo, code):
    return abo.extra_abo(code)
    
