from functools import wraps
from django.contrib import messages
from django.http import HttpResponseRedirect


def single_element_action(error_message=''):
    """ For admin actions this decorator will check that only one element is selected for the action
    """
    def decorator(action=None):
        @wraps(action)
        def wrapper(self, request, queryset):
            if queryset.count() != 1:
                self.message_user(request, error_message, level=messages.ERROR)
                return HttpResponseRedirect('')
            else:
                return action(self, request, queryset)
        return wrapper
    return decorator
