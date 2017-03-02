# -*- coding: utf-8 -*-

from datetime import date
from collections import defaultdict
from StringIO import StringIO
import string
import random
import re
import math
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.core.management import call_command
from django.db.models import Count
from django.db import models
from django.utils import timezone

import xlsxwriter

from my_ortoloco.models import *
from my_ortoloco.forms import *
from my_ortoloco.helpers import *
from my_ortoloco.filters import Filter
from my_ortoloco.mailer import *
from my_ortoloco.views import get_menu_dict

from static_ortoloco.models import StaticContent

import hashlib
from static_ortoloco.models import Politoloco

from decorators import primary_loco_of_abo


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(random.choice(chars) for x in range(size))

@login_required
def my_abo(request):
    """
    Details for an abo of a loco
    """
    renderdict = get_menu_dict(request)

    if request.user.loco.abo != None:
        current_zusatzabos = request.user.loco.abo.extra_abos.all()
        future_zusatzabos = request.user.loco.abo.future_extra_abos.filter(active=False)
        zusatzabos_changed = set(current_zusatzabos) != set(future_zusatzabos)

        if request.user.loco.abo:
            renderdict.update({
                'zusatzabos': current_zusatzabos,
                'future_zusatzabos': future_zusatzabos,
                'zusatzabos_changed': zusatzabos_changed,
                'mitabonnenten': request.user.loco.abo.bezieher_locos().exclude(email=request.user.loco.email),
                'primary': request.user.loco.abo.primary_loco.email == request.user.loco.email,
                'next_extra_abo_date': Abo.next_extra_change_date(),
                'next_size_date': Abo.next_size_change_date()
            })
    renderdict.update({
        'loco': request.user.loco,
        'scheine': request.user.loco.anteilschein_set.count(),
        'scheine_unpaid': request.user.loco.anteilschein_set.filter(paid_date=None).count(),
        'menu': {'abonnement': 'active'},
    })
    return render(request, "my_abo.html", renderdict)


@primary_loco_of_abo
def my_abo_change(request, abo_id):
    """
    Ein Abo ändern
    """
    month = int(time.strftime("%m"))
    renderdict = get_menu_dict(request)
    renderdict.update({
        'loco': request.user.loco,
        'change_size': month <= 10,
        'next_extra_abo_date': Abo.next_extra_change_date(),
        'next_size_date': Abo.next_size_change_date()
    })
    return render(request, "my_abo_change.html", renderdict)


@primary_loco_of_abo
def my_depot_change(request, abo_id):
    """
    Ein Abo-Depot ändern
    """
    saved = False
    if request.method == "POST":
        request.user.loco.abo.future_depot = get_object_or_404(Depot, id=int(request.POST.get("depot")))
        request.user.loco.abo.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'loco': request.user.loco,
        "depots": Depot.objects.all()
    })
    return render(request, "my_depot_change.html", renderdict)


@primary_loco_of_abo
def my_size_change(request, abo_id):
    """
    Eine Abo-Grösse ändern
    """
    saved = False
    if request.method == "POST" and int(time.strftime("%m")) <=10 and int(request.POST.get("abo")) > 0:
        request.user.loco.abo.future_size = int(request.POST.get("abo"))
        request.user.loco.abo.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'size': request.user.loco.abo.future_size
    })
    return render(request, "my_size_change.html", renderdict)


@primary_loco_of_abo
def my_extra_change(request, abo_id):
    """
    Ein Extra-Abos ändern
    """
    saved = False
    if request.method == "POST":
        for extra_abo in ExtraAboType.objects.all():
            existing = request.user.loco.abo.extra_abos.filter(type__id=extra_abo.id)
            if request.POST.get("abo" + str(extra_abo.id)) == str(extra_abo.id):
		if existing.count()==0:
                    future_extra_abo = ExtraAbo.create()
                    future_extra_abo.abo = request.user.loco.abo
                    future_extra_abo.type = extra_abo
                    future_extra_abo.active = False
                    future_extra_abo.save()
                else:
                    has_active=False
                    index=0;
                    while not has_active or index<existing.count():
                        existing_extra_abo = exisitng[index]
                        if existing_extra_abo.active == True:
                             has_active=True
                        elif existing_extra_abo.canceled==True and future_extra_abo.active==True:
                             existing_extra_abo.canceled=False;
                             existing_extra_abo.save();
                             has_active=True
                        index+=1
                    if not has_active:
                        future_extra_abo = ExtraAbo.create()
                        future_extra_abo.abo = request.user.loco.abo
                        future_extra_abo.type = extra_abo
                        future_extra_abo.active = False
                        future_extra_abo.save()

            else:
                if existing.count()>0:
                    for existing_extra_abo in existing:
			if existing_extra_abo.canceled==False and future_extra_abo.active==True:
                            existing_extra_abo.canceled=True;
                            existing_extra_abo.save();
                        elif existing_extra_abo.deactivation_date is None and future_extra_abo.active==False:
                            existing_extra_abo.delete();
        request.user.loco.abo.save()
        saved = True

    abos = []
    for abo in ExtraAboType.objects.all():
        if request.user.loco.abo.future_extra_abos.filter(type__id=abo.id).count()>0:
            abos.append({
                'id': abo.type.id,
                'name': abo.type.name,
                'selected': True
            })
        else:
            abos.append({
                'id': abo.type.id,
                'name': abo.type.name
            })
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'loco': request.user.loco,
        "extras": abos
    })
    return render(request, "my_extra_change.html", renderdict)


def my_signup(request):
    """
    Become a member of ortoloco
    """
    success = False
    agberror = False
    agbchecked = False
    userexists = False
    if request.method == 'POST':
        agbchecked = request.POST.get("agb") == "on"

        locoform = ProfileLocoForm(request.POST)
        if not agbchecked:
            agberror = True
        else:
            if locoform.is_valid():
                #check if user already exists
                if User.objects.filter(email=locoform.cleaned_data['email']).__len__() > 0:
                    userexists = True
                else:
                    #set all fields of user
                    #email is also username... we do not use it
                    password = password_generator()

                    loco = Loco.objects.create(first_name=locoform.cleaned_data['first_name'], last_name=locoform.cleaned_data['last_name'], email=locoform.cleaned_data['email'])
                    loco.addr_street = locoform.cleaned_data['addr_street']
                    loco.addr_zipcode = locoform.cleaned_data['addr_zipcode']
                    loco.addr_location = locoform.cleaned_data['addr_location']
                    loco.phone = locoform.cleaned_data['phone']
                    loco.mobile_phone = locoform.cleaned_data['mobile_phone']
                    loco.save()

                    loco.user.set_password(password)
                    loco.user.save()

                    #log in to allow him to make changes to the abo
                    loggedin_user = authenticate(username=loco.user.username, password=password)
                    login(request, loggedin_user)
                    success = True
                    return redirect("/my/aboerstellen")
    else:
        locoform = ProfileLocoForm()

    renderdict = {
        'locoform': locoform,
        'success': success,
        'agberror': agberror,
        'agbchecked': agbchecked,
        'userexists': userexists,
        'menu': {'join': 'active'},
    }
    return render(request, "signup.html", renderdict)


@login_required
def my_add_loco(request, abo_id):
    scheineerror = False
    scheine = 1
    userexists = False
    if request.method == 'POST':
        locoform = ProfileLocoForm(request.POST)
        if User.objects.filter(email=request.POST.get('email')).__len__() > 0:
            userexists = True
        try:
            scheine = int(request.POST.get("anteilscheine"))
            scheineerror = scheine < 0
        except TypeError:
            scheineerror = True
        except  ValueError:
            scheineerror = True
        if locoform.is_valid() and scheineerror is False and userexists is False:
            username = make_username(locoform.cleaned_data['first_name'],
                                     locoform.cleaned_data['last_name'],
                                     locoform.cleaned_data['email'])
            pw = password_generator()
            loco = Loco.objects.create(first_name=locoform.cleaned_data['first_name'], last_name=locoform.cleaned_data['last_name'], email=locoform.cleaned_data['email'])
            loco.first_name = locoform.cleaned_data['first_name']
            loco.last_name = locoform.cleaned_data['last_name']
            loco.email = locoform.cleaned_data['email']
            loco.addr_street = locoform.cleaned_data['addr_street']
            loco.addr_zipcode = locoform.cleaned_data['addr_zipcode']
            loco.addr_location = locoform.cleaned_data['addr_location']
            loco.phone = locoform.cleaned_data['phone']
            loco.mobile_phone = locoform.cleaned_data['mobile_phone']
            loco.confirmed = False
            loco.abo_id = abo_id
            loco.save()

            loco.user.set_password(pw)
            loco.user.save()

            for num in range(0, scheine):
                anteilschein = Anteilschein(loco=loco, paid_date=None)
                anteilschein.save()
                send_anteilschein_created_mail(anteilschein, request.META["HTTP_HOST"])
            send_been_added_to_abo(loco.email, pw, request.user.loco.get_name(), scheine, hashlib.sha1(locoform.cleaned_data['email'] + str(abo_id)).hexdigest(), request.META["HTTP_HOST"])

            loco.save()
            if request.GET.get("return"):
                return redirect(request.GET.get("return"))
            return redirect('/my/aboerstellen')

    else:
        loco = request.user.loco
        initial = {"addr_street": loco.addr_street,
                   "addr_zipcode": loco.addr_zipcode,
                   "addr_location": loco.addr_location,
                   "phone": loco.phone,
        }
        locoform = ProfileLocoForm(initial=initial)
    renderdict = {
        'scheine': scheine,
        'userexists': userexists,
        'scheineerror': scheineerror,
        'locoform': locoform,
        "loco": request.user.loco,
        "depots": Depot.objects.all(),
        "cancelUrl": request.GET.get("return")
    }
    return render(request, "add_loco.html", renderdict)


@login_required
def my_createabo(request):
    """
    Abo erstellen
    """
    loco = request.user.loco
    scheineerror = False
    aboform = AboForm()

    if loco.abo is None:
        selectedabo="none"
    else:
        selectedabo = AboSize.objects.filter(size=loco.abo.size)[0].name

    loco_scheine = 0
    if loco.abo is not None:
        for abo_loco in loco.abo.bezieher_locos().exclude(email=request.user.loco.email):
            loco_scheine += abo_loco.anteilschein_set.all().__len__()

    if request.method == "POST":
        scheine = int(request.POST.get("scheine"))
        selectedabo = request.POST.get("abo")
        aboform = AboForm(request.POST)

        scheine += loco_scheine
        min_anzahl_scheine = next(iter(AboSize.objects.filter(name=selectedabo).values_list('shares', flat=True) or []), 1)
        if scheine < min_anzahl_scheine and not aboform.is_valid():
            scheineerror = True
        else:
            depot = Depot.objects.all().filter(id=request.POST.get("depot"))[0]
            size = next(iter(AboSize.objects.filter(name=selectedabo).values_list('size', flat=True) or []), 0)

            if size > 0:
                if loco.abo is None:
                    loco.abo = Abo.objects.create(size=size, primary_loco=loco, depot=depot)
                else:
                    loco.abo.size = size
                    loco.abo.future_size = size
                    loco.abo.depot = depot
                loco.abo.save()
            loco.save()

            if loco.anteilschein_set.count() < int(request.POST.get("scheine")):
                toadd = int(request.POST.get("scheine")) - loco.anteilschein_set.count()
                for num in range(0, toadd):
                    anteilschein = Anteilschein(loco=loco, paid_date=None)
                    anteilschein.save()
                    send_anteilschein_created_mail(anteilschein, request.META["HTTP_HOST"])
            if request.POST.get("add_loco"):
                return redirect("/my/abonnent/" + str(loco.abo_id))
            else:
                password = password_generator()

                request.user.set_password(password)
                request.user.save()

                #user did it all => send confirmation mail
                send_welcome_mail(loco.email, password, request.META["HTTP_HOST"])
                send_welcome_mail("dorothea@ortoloco.ch", "<geheim>", request.META["HTTP_HOST"])

                return redirect("/my/willkommen")

    selected_depot = None
    mit_locos = []
    if request.user.loco.abo is not None:
        selected_depot = request.user.loco.abo.depot
        mit_locos = request.user.loco.abo.bezieher_locos().exclude(email=request.user.loco.email)

    renderdict = {
        'loco_scheine': loco_scheine,
        'loco': request.user.loco,
        'abo_sizes': AboSize.objects.order_by('size'),
        'depots': Depot.objects.all(),
        'selected_depot': selected_depot,
        'selected_abo': selectedabo,
        'scheineerror': scheineerror,
        'mit_locos': mit_locos,
        'aboform': aboform
    }
    return render(request, "createabo.html", renderdict)


@login_required
def my_welcome(request):
    """
    Willkommen
    """

    renderdict = get_menu_dict(request)
    renderdict.update({
        'jobs': get_current_jobs()[:7],
        'teams': Taetigkeitsbereich.objects.filter(hidden=False),
        'no_abo': request.user.loco.abo is None
    })

    return render(request, "welcome.html", renderdict)


def my_confirm(request, hash):
    """
    Confirm from a user that has been added as a Mitabonnent
    """

    for loco in Loco.objects.all():
        if hash == hashlib.sha1(loco.email + str(loco.abo_id)).hexdigest():
            loco.confirmed = True
            loco.save()

    return redirect("/my/home")








