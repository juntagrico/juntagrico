from django.shortcuts import redirect
from django.urls import reverse


def return_to_previous_location(request):
    if request.META.get('HTTP_REFERER') is not None:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(reverse('home'))
