# -*- coding: utf-8 -*-

from django import forms
from django.utils.html import format_html


class MyHTMLWidget(forms.widgets.Widget):
    '''
    Widget that display (non-editably) arbitrary html.
    '''

    def render(self, name, value, attrs=None,  renderer=None,):
        if value is None:
            return ''
        return format_html(value)
