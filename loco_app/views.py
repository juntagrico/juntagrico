from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from loco_app.models import *


def list_depots(request):
    """
    Simple test view.
    """
    depot_list = Depot.objects.filter()

    renderdict = {
        'depots': depot_list,
    }

    return render(request, "depots.html", renderdict)

