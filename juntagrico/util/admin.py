# -*- coding: utf-8 -*-

from django import forms
from django.utils.html import format_html


class MyHTMLWidget(forms.widgets.Widget):
    '''
    Widget that display (non-editably) arbitrary html.
    '''

    def render(self, name, value, attrs=None):
        if value is None:
            # This is needed because admin sometimes doesn't supply a value,
            # e.g. when a bad input in some other field causes the form to re-render with error
            # messages
            return ''
        return format_html(value)
