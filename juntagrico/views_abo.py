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

from decorators import primary_member_of_subscription


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(random.choice(chars) for x in range(size))

@login_required
def my_subscription(request):
    """
    Details for an subscription of a member
    """
    renderdict = get_menu_dict(request)

    if request.user.member.subscription != None:
        current_extrasubscriptions = request.user.member.subscription.extra_subscriptions.all()
        future_extrasubscriptions = request.user.member.subscription.future_extra_subscriptions.filter(active=False)
        extrasubscriptions_changed = set(current_extrasubscriptions) != set(future_extrasubscriptions)

        if request.user.member.subscription:
            renderdict.update({
                'extrasubscriptions': current_extrasubscriptions,
                'future_extrasubscriptions': future_extrasubscriptions,
                'extrasubscriptions_changed': extrasubscriptions_changed,
                'subscriptionmembers': request.user.member.subscription.recipients().exclude(email=request.user.member.email),
                'primary': request.user.member.subscription.primary_member.email == request.user.member.email,
                'next_extra_subscription_date': Subscription.next_extra_change_date(),
                'next_size_date': Subscription.next_size_change_date()
            })
    renderdict.update({
        'member': request.user.member,
        'shares': request.user.member.share_set.count(),
        'shares_unpaid': request.user.member.share_set.filter(paid_date=None).count(),
        'menu': {'subscriptionnnement': 'active'},
    })
    return render(request, "my_subscription.html", renderdict)


@primary_member_of_subscription
def my_subscription_change(request, subscription_id):
    """
    change an subscription
    """
    month = int(time.strftime("%m"))
    renderdict = get_menu_dict(request)
    renderdict.update({
        'member': request.user.member,
        'change_size': month <= 10,
        'next_extra_subscription_date': Subscription.next_extra_change_date(),
        'next_size_date': Subscription.next_size_change_date()
    })
    return render(request, "my_subscription_change.html", renderdict)


@primary_member_of_subscription
def my_depot_change(request, subscription_id):
    """
    change a depot
    """
    saved = False
    if request.method == "POST":
        request.user.member.subscription.future_depot = get_object_or_404(Depot, id=int(request.POST.get("depot")))
        request.user.member.subscription.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'member': request.user.member,
        "depots": Depot.objects.all()
    })
    return render(request, "my_depot_change.html", renderdict)


@primary_member_of_subscription
def my_size_change(request, subscription_id):
    """
    change the size of an subscription
    """
    saved = False
    if request.method == "POST" and int(time.strftime("%m")) <=10 and int(request.POST.get("subscription")) > 0:
        request.user.member.subscription.future_size = int(request.POST.get("subscription"))
        request.user.member.subscription.save()
        saved = True
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'size': request.user.member.subscription.future_size
    })
    return render(request, "my_size_change.html", renderdict)


@primary_member_of_subscription
def my_extra_change(request, subscription_id):
    """
    change an extra subscription
    """
    saved = False
    if request.method == "POST":
        for extra_subscription in ExtraSubscriptionType.objects.all():
            existing = request.user.member.subscription.extra_subscriptions.filter(type__id=extra_subscription.id)
            if request.POST.get("subscription" + str(extra_subscription.id)) == str(extra_subscription.id):
		if existing.count()==0:
                    future_extra_subscription = ExtraSubscription.create()
                    future_extra_subscription.subscription = request.user.member.subscription
                    future_extra_subscription.type = extra_subscription
                    future_extra_subscription.active = False
                    future_extra_subscription.save()
                else:
                    has_active=False
                    index=0;
                    while not has_active or index<existing.count():
                        existing_extra_subscription = existing[index]
                        if existing_extra_subscription.active == True:
                             has_active=True
                        elif existing_extra_subscription.canceled==True and future_extra_subscription.active==True:
                             existing_extra_subscription.canceled=False;
                             existing_extra_subscription.save();
                             has_active=True
                        index+=1
                    if not has_active:
                        future_extra_subscription = ExtraSubscription.create()
                        future_extra_subscription.subscription = request.user.member.subscription
                        future_extra_subscription.type = extra_subscription
                        future_extra_subscription.active = False
                        future_extra_subscription.save()

            else:
                if existing.count()>0:
                    for existing_extra_subscription in existing:
			if existing_extra_subscription.canceled==False and future_extra_subscription.active==True:
                            existing_extra_subscription.canceled=True;
                            existing_extra_subscription.save();
                        elif existing_extra_subscription.deactivation_date is None and future_extra_subscription.active==False:
                            existing_extra_subscription.delete();
        request.user.member.subscription.save()
        saved = True

    subscriptions = []
    for subscription in ExtraSubscriptionType.objects.all():
        if request.user.member.subscription.future_extra_subscriptions.filter(type__id=subscription.id).count()>0:
            subscriptions.append({
                'id': subscription.type.id,
                'name': subscription.type.name,
                'selected': True
            })
        else:
            subscriptions.append({
                'id': subscription.type.id,
                'name': subscription.type.name
            })
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'member': request.user.member,
        "extras": subscriptions
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

                    #log in to allow him to make changes to the subscription
                    loggedin_user = authenticate(username=member.user.username, password=password)
                    login(request, loggedin_user)
                    success = True
                    return redirect("/my/subscriptionerstellen")
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
def my_add_member(request, subscription_id):
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
            if member.subscription is not None:
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
            member.subscription_id = subscription_id
            member.save()
            member.user.set_password(pw)
            member.user.save()

            for num in range(0, shares):
                share = Share(member=member, paid_date=None)
                share.save()
                send_share_created_mail(share, request.METAbo["HTTP_HOST"])
            send_been_added_to_subscription(member.email, pw, request.user.member.get_name(), shares, hashlib.sha1(memberform.cleaned_data['email'] + str(subscription_id)).hexdigest(), request.METAbo["HTTP_HOST"])

            member.save()
            if request.GET.get("return"):
                return redirect(request.GET.get("return"))
            return redirect('/my/subscriptionerstellen')
        if  memberexists is True and memberblocked is False:
            member.subscription_id=subscription_id
            member.save()
            if request.GET.get("return"):
                return redirect(request.GET.get("return"))
            return redirect('/my/subscriptionerstellen')
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
def my_createsubscription(request):
    """
    create a subscription
    """
    member = request.user.member
    shareerror = False
    subscriptionform = SubscriptionForm()

    if member.subscription is None:
        selectedsubscription="none"
    else:
        selectedsubscription = SubscriptionSize.objects.filter(size=member.subscription.size)[0].name

    member_shares = 0
    if member.subscription is not None:
        for subscription_member in member.subscription.recipients().exclude(email=request.user.member.email):
            member_shares += subscription_member.share_set.all().__len__()

    if request.method == "POST":
        shares = int(request.POST.get("shares"))
        selectedsubscription = request.POST.get("subscription")
        subscriptionform = SubscriptionForm(request.POST)

        shares += member_shares
        min_num_shares = next(iter(SubscriptionSize.objects.filter(name=selectedsubscription).values_list('shares', flat=True) or []), 1)
        if shares < min_num_shares or not subscriptionform.is_valid():
            shareerror = shares < min_num_shares
        else:
            depot = Depot.objects.all().filter(id=request.POST.get("depot"))[0]
            size = next(iter(SubscriptionSize.objects.filter(name=selectedsubscription).values_list('size', flat=True) or []), 0)

            if size > 0:
                if member.subscription is None:
                    member.subscription = Subscription.objects.create(size=size, primary_member=member, depot=depot,start_date=subscriptionform.cleaned_data['start_date'])
                else:
                    member.subscription.start_date=subscriptionform.cleaned_data['start_date']
                    member.subscription.size = size
                    member.subscription.future_size = size
                    member.subscription.depot = depot
                member.subscription.save()
            member.save()

            if member.share_set.count() < int(request.POST.get("shares")):
                toadd = int(request.POST.get("shares")) - member.share_set.count()
                for num in range(0, toadd):
                    share = Share(member=member, paid_date=None)
                    share.save()
                    send_share_created_mail(share, request.METAbo["HTTP_HOST"])
            if request.POST.get("add_member"):
                return redirect("/my/subscriptionnnent/" + str(member.subscription_id))
            else:
                password = password_generator()
                request.user.set_password(password)
                request.user.save()
                #user did it all => send confirmation mail
                send_welcome_mail(member.email, password, request.METAbo["HTTP_HOST"])

                return redirect("/my/willkommen")

    selected_depot = None
    co_members = []
    if request.user.member.subscription is not None:
        selected_depot = request.user.member.subscription.depot
        co_members = request.user.member.subscription.recipients().exclude(email=request.user.member.email)

    renderdict = {
        'member_shares': member_shares,
        'member': request.user.member,
        'subscription_sizes': SubscriptionSize.objects.order_by('size'),
        'depots': Depot.objects.all(),
        'selected_depot': selected_depot,
        'selected_subscription': selectedsubscription,
        'shareerror': shareerror,
        'co_members': co_members,
        'subscriptionform': subscriptionform
    }
    return render(request, "createsubscription.html", renderdict)


@login_required
def my_welcome(request):
    """
    welcome
    """

    renderdict = get_menu_dict(request)
    renderdict.update({
        'jobs': get_current_jobs()[:7],
        'teams': AboctivityAborea.objects.filter(hidden=False),
        'no_subscription': request.user.member.subscription is None
    })

    return render(request, "welcome.html", renderdict)


def my_confirm(request, hash):
    """
    Confirm from a user that has been added as a co_subscriptionnnent
    """

    for member in Member.objects.all():
        if hash == hashlib.sha1(member.email + str(member.subscription_id)).hexdigest():
            member.confirmed = True
            member.save()

    return redirect("/my/home")
