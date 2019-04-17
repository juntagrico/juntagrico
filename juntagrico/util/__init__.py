from django.shortcuts import redirect

from juntagrico.config import Config


def return_to_previous_location(request):
    if request.META.get('HTTP_REFERER') is not None:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('http://' + Config.adminportal_server_url())
