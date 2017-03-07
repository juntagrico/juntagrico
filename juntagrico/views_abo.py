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

from juntagrico.models import *
from juntagrico.forms import *
from juntagrico.helpers import *
from juntagrico.filters import Filter
from juntagrico.mailer import *
from juntagrico.views import get_menu_dict
from juntagrico.config import *
import hashlib

from decorators import primary_member_of_abo


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(random.choice(chars) for x in range(size))

@login_required
def my_abo(request):
    """
    Details for an abo of a member
    """
    renderdict = get_menu_dict(request)

    if request.user.member.abo != None:
        current_extraabos = request.user.member.abo.extra_abos.all()
        future_extraabos = request.user.member.abo.future_extra_abos.filter(active=False)
        extraabos_changed = set(current_extraabos) != set(future_extraabos)

        if request.user.member.abo:
            renderdict.update({
                'extraabos': current_extraabos,
                'future_extraabos': future_extraabos,
                'extraabos_changed': extraabos_changed,
                'abomembers': request.user.member.abo.recipients().exclude(email=request.user.member.email),
                'primary': request.user.member.abo.primary_member.email == request.user.member.email,
                'next_extra_abo_date': Abo.next_extra_change_date(),
                'next_size_date': Abo.next_size_change_date()
            })
    renderdict.update({
        'member': request.user.member,
        'shares': request.user.member.share_set.count(),
        'shares_unpaid': request.user.member.share_set.filter(paid_date=None).count(),
        'menu': {'abonnement': 'active'},
    })
    return render(request, "my_abo.html", renderdict)


@primary_member_of_abo
def my_abo_change(request, abo_id):
    """
    change an abo
    """
    month = int(time.strftime("%m"))
    renderdict = get_menu_dict(request)
    renderdict.update({
        'member': request.user.member,
        'change_size': month <= 10,
        'next_extra_abo_date': Abo.next_extra_change_date(),
        'next_size_date': Abo.next_size_change_date()
    })
    return render(request, "my_abo_change.html", renderdict)


@primary_member_of_abo
def my_depot_change(request, abo_id):
    """
    change a depot
    """
    saved = False
    if request.method == "POST":
        request.user.member.abo.future_depot = get_object_or_404(Depot, id=int(request.POST.get("depot")))
        request.user.member.abo.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'member': request.user.member,
        "depots": Depot.objects.all()
    })
    return render(request, "my_depot_change.html", renderdict)


@primary_member_of_abo
def my_size_change(request, abo_id):
    """
    change the size of an abo
    """
    saved = False
    if request.method == "POST" and int(time.strftime("%m")) <=10 and int(request.POST.get("abo")) > 0:
        request.user.member.abo.future_size = int(request.POST.get("abo"))
        request.user.member.abo.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'size': request.user.member.abo.future_size
    })
    return render(request, "my_size_change.html", renderdict)


@primary_member_of_abo
def my_extra_change(request, abo_id):
    """
    change an extra abo
    """
    saved = False
    if request.method == "POST":
        for extra_abo in ExtraAboType.objects.all():
            existing = request.user.member.abo.extra_abos.filter(type__id=extra_abo.id)
            if request.POST.get("abo" + str(extra_abo.id)) == str(extra_abo.id):
		if existing.count()==0:
                    future_extra_abo = ExtraAbo.create()
                    future_extra_abo.abo = request.user.member.abo
                    future_extra_abo.type = extra_abo
                    future_extra_abo.active = False
                    future_extra_abo.save()
                else:
                    has_active=False
                    index=0;
                    while not has_active or index<existing.count():
                        existing_extra_abo = existing[index]
                        if existing_extra_abo.active == True:
                             has_active=True
                        elif existing_extra_abo.canceled==True and future_extra_abo.active==True:
                             existing_extra_abo.canceled=False;
                             existing_extra_abo.save();
                             has_active=True
                        index+=1
                    if not has_active:
                        future_extra_abo = ExtraAbo.create()
                        future_extra_abo.abo = request.user.member.abo
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
        request.user.member.abo.save()
        saved = True

    abos = []
    for abo in ExtraAboType.objects.all():
        if request.user.member.abo.future_extra_abos.filter(type__id=abo.id).count()>0:
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
        'member': request.user.member,
        "extras": abos
    })
    return render(request, "my_extra_change.html", renderdict)


def my_signup(request):
    """
    Become a member of juntagrico
    """
    success = False
    agberror = False
    agbchecked = False
    userexists = False
    if request.method == 'POST':
        agbchecked = request.POST.get("agb") == "on"

        memberform = MemberProfileForm(request.POST)
        if not agbchecked:
            agberror = True
        else:
            if memberform.is_valid():
                #check if user already exists
                if User.objects.filter(email=memberform.cleaned_data['email']).__len__() > 0:
                    userexists = True
                else:
                    #set all fields of user
                    #email is also username... we do not use it
                    password = password_generator()

                    member = Member.objects.create(first_name=memberform.cleaned_data['first_name'], last_name=memberform.cleaned_data['last_name'], email=memberform.cleaned_data['email'])
                    member.addr_street = memberform.cleaned_data['addr_street']
                    member.addr_zipcode = memberform.cleaned_data['addr_zipcode']
                    member.addr_location = memberform.cleaned_data['addr_location']
                    member.phone = memberform.cleaned_data['phone']
                    member.mobile_phone = memberform.cleaned_data['mobile_phone']
                    member.save()

                    member.user.set_password(password)
                    member.user.save()

                    #log in to allow him to make changes to the abo
                    loggedin_user = authenticate(username=member.user.username, password=password)
                    login(request, loggedin_user)
                    success = True
                    return redirect("/my/aboerstellen")
    else:
        memberform = MemberProfileForm()

    renderdict = {
        'memberform': memberform,
        'success': success,
        'agberror': agberror,
        'agbchecked': agbchecked,
        'userexists': userexists,
        'menu': {'join': 'active'},
    }
    return render(request, "signup.html", renderdict)


@login_required
def my_add_member(request, abo_id):
    shareerror = False
    shares = 1
    memberexists = False
    memberblocked = False
    member = False
    if request.method == 'POST':
        memberform = MemberProfileForm(request.POST)
        members = Member.objects.filter(email=request.POST.get('email'))
        if members.count() > 0:
            memberexists = True
            member= members[0]
            if member.abo is not None:
                memberblocked=True
        try:
            shares = int(request.POST.get("shares"))
            shareerror = shares < 0
        except TypeError:
            shareerror = True
        except  ValueError:
            shareerror = True
        if memberform.is_valid() and shareerror is False and memberexists is False:
            pw = password_generator()
            member = Member.objects.create(first_name=memberform.cleaned_data['first_name'], last_name=memberform.cleaned_data['last_name'], email=memberform.cleaned_data['email'])
            member.first_name = memberform.cleaned_data['first_name']
            member.last_name = memberform.cleaned_data['last_name']
            member.email = memberform.cleaned_data['email']
            member.addr_street = memberform.cleaned_data['addr_street']
            member.addr_zipcode = memberform.cleaned_data['addr_zipcode']
            member.addr_location = memberform.cleaned_data['addr_location']
            member.phone = memberform.cleaned_data['phone']
            member.mobile_phone = memberform.cleaned_data['mobile_phone']
            member.confirmed = False
            member.abo_id = abo_id
            member.save()
            member.user.set_password(pw)
            member.user.save()

            for num in range(0, shares):
                share = Share(member=member, paid_date=None)
                share.save()
                send_share_created_mail(share, request.META["HTTP_HOST"])
            send_been_added_to_abo(member.email, pw, request.user.member.get_name(), shares, hashlib.sha1(memberform.cleaned_data['email'] + str(abo_id)).hexdigest(), request.META["HTTP_HOST"])

            member.save()
            if request.GET.get("return"):
                return redirect(request.GET.get("return"))
            return redirect('/my/aboerstellen')
        if  memberexists is True and memberblocked is False:
            member.abo_id=abo_id
            member.save()
            if request.GET.get("return"):
                return redirect(request.GET.get("return"))
            return redirect('/my/aboerstellen')
    else:
        member = request.user.member
        initial = {"addr_street": member.addr_street,
                   "addr_zipcode": member.addr_zipcode,
                   "addr_location": member.addr_location,
                   "phone": member.phone,
        }
        memberform = MemberProfileForm(initial=initial)
    renderdict = {
        'shares': shares,
        'memberexists': memberexists,
        'memberblocked': memberexists,
        'shareerror': shareerror,
        'memberform': memberform,
        "member": request.user.member,
        "depots": Depot.objects.all(),
        "cancelUrl": request.GET.get("return")
    }
    return render(request, "add_member.html", renderdict)


@login_required
def my_createabo(request):
    """
    create a abo
    """
    member = request.user.member
    shareerror = False
    aboform = AboForm()

    if member.abo is None:
        selectedabo="none"
    else:
        selectedabo = AboSize.objects.filter(size=member.abo.size)[0].name

    member_shares = 0
    if member.abo is not None:
        for abo_member in member.abo.recipients().exclude(email=request.user.member.email):
            member_shares += abo_member.share_set.all().__len__()

    if request.method == "POST":
        shares = int(request.POST.get("shares"))
        selectedabo = request.POST.get("abo")
        aboform = AboForm(request.POST)

        shares += member_shares
        min_num_shares = next(iter(AboSize.objects.filter(name=selectedabo).values_list('shares', flat=True) or []), 1)
        if shares < min_num_shares or not aboform.is_valid():
            shareerror = shares < min_num_shares
        else:
            depot = Depot.objects.all().filter(id=request.POST.get("depot"))[0]
            size = next(iter(AboSize.objects.filter(name=selectedabo).values_list('size', flat=True) or []), 0)

            if size > 0:
                if member.abo is None:
                    member.abo = Abo.objects.create(size=size, primary_member=member, depot=depot,start_date=aboform.cleaned_data['start_date'])
                else:
                    member.abo.start_date=aboform.cleaned_data['start_date']
                    member.abo.size = size
                    member.abo.future_size = size
                    member.abo.depot = depot
                member.abo.save()
            member.save()

            if member.share_set.count() < int(request.POST.get("shares")):
                toadd = int(request.POST.get("shares")) - member.share_set.count()
                for num in range(0, toadd):
                    share = Share(member=member, paid_date=None)
                    share.save()
                    send_share_created_mail(share, request.META["HTTP_HOST"])
            if request.POST.get("add_member"):
                return redirect("/my/abonnent/" + str(member.abo_id))
            else:
                password = password_generator()
                request.user.set_password(password)
                request.user.save()
                #user did it all => send confirmation mail
                send_welcome_mail(member.email, password, request.META["HTTP_HOST"])

                return redirect("/my/willkommen")

    selected_depot = None
    co_members = []
    if request.user.member.abo is not None:
        selected_depot = request.user.member.abo.depot
        co_members = request.user.member.abo.recipients().exclude(email=request.user.member.email)

    renderdict = {
        'member_shares': member_shares,
        'member': request.user.member,
        'abo_sizes': AboSize.objects.order_by('size'),
        'depots': Depot.objects.all(),
        'selected_depot': selected_depot,
        'selected_abo': selectedabo,
        'shareerror': shareerror,
        'co_members': co_members,
        'aboform': aboform
    }
    return render(request, "createabo.html", renderdict)


@login_required
def my_welcome(request):
    """
    welcome
    """

    renderdict = get_menu_dict(request)
    renderdict.update({
        'jobs': get_current_jobs()[:7],
        'teams': ActivityArea.objects.filter(hidden=False),
        'no_abo': request.user.member.abo is None
    })

    return render(request, "welcome.html", renderdict)


def my_confirm(request, hash):
    """
    Confirm from a user that has been added as a co_abonnent
    """

    for member in Member.objects.all():
        if hash == hashlib.sha1(member.email + str(member.abo_id)).hexdigest():
            member.confirmed = True
            member.save()

    return redirect("/my/home")
