from collections import defaultdict, Counter

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.forms.models import modelformset_factory
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.forms import ModelForm

from django.forms import ModelForm

from static_ortoloco.models import *
import os
import time, json, base64, hmac, sha, urllib
from django.utils import simplejson

# Create your views here.

def home(request):
    """
    Homepage of "static" page
    """

    renderdict = {
        'submenu': get_object_or_404(StaticContent, name='HomeUnterMenu'),
        #'homeTitel': get_object_or_404(StaticContent, name='HomeTitel'),
        #'homeText': get_object_or_404(StaticContent, name='HomeText'),
        'menu': {
            'home': 'active'
        }
    }

    return render(request, "home.html", renderdict)


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

    return render(request, "about.html", renderdict)


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

    return render(request, "portrait.html", renderdict)


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

    return render(request, "background.html", renderdict)


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

    return render(request, "abo.html", renderdict)


def faq(request):
    """
    FAQ ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'faq': 'active'
        }
    }

    return render(request, "faq.html", renderdict)


def join(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'join': 'active'
        }
    }

    return render(request, "join.html", renderdict)


def media(request):
    """
    About ortoloco of "static" page
    """
    medias_list = Media.objects.all().order_by('year').reverse()
    renderdict = {
        'menu': {
            'media': 'active'
        },
        'medias': medias_list,
    }

    return render(request, "media.html", renderdict)


def links(request):
    """
    Links to partners
    """
    links_list = Link.objects.all().reverse()

    renderdict = {
        'menu': {
            'links': 'active'
        },
        'links': links_list,
    }

    return render(request, "links.html", renderdict)


def downloads(request):
    """
    Downloads available
    """
    download_list = Download.objects.all().reverse()

    renderdict = {
        'menu': {
            'downloads': 'active'
        },
        'downloads': download_list,
    }

    return render(request, "downloads.html", renderdict)


def contact(request):
    """
    Contact page
    """
    class PolitolocoForm(ModelForm):
        class Meta:
            model = Politoloco
            fields = ['email']

    success = 0
    failure = 0
    message = ''

    f = PolitolocoForm()
    if request.method == 'POST':
        add_f = PolitolocoForm(request.POST)
        if add_f.is_valid():
            add_f.save()
            success = 1
            message = 'E-Mail Adresse beim Newsletter von Politoloco registriert.'
        else:
            failure = 1
            message = 'E-Mail Adresse ungueltig'

    renderdict = {
        'menu': {
            'contact': 'active',
        },
        'request': request,
        'success': success,
        'failure': failure,
        'message': message
    }

    return render(request, "contact.html", renderdict)
