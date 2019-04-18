from django import forms
from django.utils.html import format_html


def queryset_for_coordinator(request, field_name, perm, query_function, **kwargs):
    if field_name == 'type' and request.user.has_perm(perm) and (
            not (request.user.is_superuser or
                 request.user.has_perm('juntagrico.is_operations_group'))):
        kwargs['queryset'] = query_function(request.user.member)
    return kwargs


class MyHTMLWidget(forms.widgets.Widget):
    '''
    Widget that display (non-editably) arbitrary html.
    '''

    def render(self, name, value, attrs=None,  renderer=None,):
        if value is None:
            return ''
        return format_html(value)
