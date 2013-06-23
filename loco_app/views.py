from collections import defaultdict, Counter

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from loco_app.models import *


def home(request):
    """
    Homepage of "static" page
    """
    
    renderdict = {
        'submenu': get_object_or_404(StaticContent, name='HomeUnterMenu'),
        'homeTitel': get_object_or_404(StaticContent, name='HomeTitel'),
        'homeText': get_object_or_404(StaticContent, name='HomeText'),
        'menu': {
            'home': 'active'
        }
    }

    return render(request, "web/home.html", renderdict)

def about(request):
    """
    About ortoloco of "static" page
    """
    
    renderdict = {
        'menu': {
            'about': 'active',
            'aboutChild': 'active'
        }
    }

    return render(request, "web/about.html", renderdict)

def portrait(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'portrait': 'active'
        }
    }

    return render(request, "web/portrait.html", renderdict)

def background(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'background': 'active'
        }
    }

    return render(request, "web/background.html", renderdict)

def abo(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'abo': 'active'
        }
    }

    return render(request, "web/abo.html", renderdict)

def join(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'join': 'active'
        }
    }

    return render(request, "web/join.html", renderdict)

def gallery(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'gallery': 'active'
        }
    }

    return render(request, "web/gallery.html", renderdict)

def media(request):
    """
    About ortoloco of "static" page
    """
    medias_list = Medias.objects.all().order_by('year').reverse()
    renderdict = {
        'menu': {
            'media': 'active'
        },
        'medias': medias_list,
    }

    return render(request, "web/media.html", renderdict)

def downloads(request):
    """
    Downloads available
    """

    renderdict = {
        'menu': {
            'downloads': 'active'
        },
        'downloads': download_list,
    }

    return render(request, "web/downloads.html", renderdict)


def all_depots(request):
    """
    Simple test view.
    """
    depot_list = Depot.objects.all()

    renderdict = {
        'depots': depot_list,
    }
    return render(request, "depots.html", renderdict)


def depot_list(request, name_or_id):
    """
    Create table of users and their abos for a specific depot.

    Should be able to generate pdfs and spreadsheets in the future.
    """

    # old code, needs to be fixed
    return HttpResponse("WIP")

    if name_or_id.isdigit():
        depot = get_object_or_404(Depot, id=int(name_or_id))
    else:
        depot = get_object_or_404(Depot, name=name_or_id.lower())

    # get all abos of this depot
    abos = Abo.objects.filter(depot=depot)

    # helper function to format set of locos consistently
    def locos_to_str(locos):
        # TODO: use first and last name
        locos = sorted(loco.user.username for loco in locos)
        return u", ".join(locos)

    # accumulate abos by sets of locos, e.g. Vitor: klein x1, gross: x0, eier x1
    # d is a dictionary of counters, which count the number of each abotype for a given set of users.
    d = defaultdict(Counter)
    for abo in abos:
        d[locos_to_str(abo.locos.all())][abo.abotype] += 1

    # build rows of data.
    abotypes = AboType.objects.all()
    header = ["Personen"]
    header.extend(i.name for i in abotypes)
    header.append("abgeholt")
    data = []
    for (locos, counter) in sorted(d.items()):
        row = [locos]
        row.extend(counter[i] for i in abotypes)
        data.append(row)


    renderdict = {
        "depot": depot,
        "table_header": header,
        "table_data": data,
    }
    return render(request, "depot_list.html", renderdict)
    
