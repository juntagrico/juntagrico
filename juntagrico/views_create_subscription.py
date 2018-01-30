# -*- coding: utf-8 -*-

import random
import string

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.decorators import primary_member_of_subscription
from juntagrico.forms import *
from juntagrico.models import *
from juntagrico.views import get_menu_dict
from juntagrico.util import temporal
from juntagrico.util.management import *


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(
    random.choice(chars) for x in range(size))


def cs_welcome(request):
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    
    renderdict= {
        'no_subscription': member.future_subscription is None
    }

    return render(request, 'welcome.html', renderdict)


def cs_select_subscription(request):
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    if request.method == 'POST':
        selectedsubscription = request.POST.get('subscription')
        size = next(
                iter(SubscriptionTypeDao.get_by_id(selectedsubscription).values_list('size__size', flat=True) or []),
                0)
        if size > 0:
            request.session['selectedsubscription'] = selectedsubscription
            redirect('/my/create/subscription/selectdepot')
        redirect('/my/create/subscription/shares')
    renderdict = {    
        'hours_used': Config.assignment_unit()=='HOURS',
        'subscription_sizes': SubscriptionSizeDao.all_sizes_ordered(),
    }
    return render(request, 'createsubscription/select_subscription.html', renderdict)

    
def cs_select_depot(request):
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    if request.method == 'POST':
        depot = DepotDao.depot_by_id(request.POST.get('depot'))
        request.session['selecteddepot'] = depot
        redirect('/my/create/subscription/start')
    renderdict = {
        'member': member,
        'depots': DepotDao.all_depots(),
    }
    return render(request, 'createsubscription/select_depot.html', renderdict)


def cs_select_start_date(request):
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    subscriptionform = SubscriptionForm()
    if request.method == 'POST':
        subscriptionform = SubscriptionForm(request.POST)
        if subscriptionform.is_valid():
            request.session['start_date'] = subscriptionform.cleaned_data['start_date']
            redirect('/my/create/subscription/addmembers')
    renderdict = {      
        'subscriptionform': subscriptionform,
    }
    return render(request, 'createsubscription/select_start_date.html', renderdict)

    
def cs_select_shares(request):
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    share_error=False
    share_sum = member.active_shares    
    co_members = request.session.get('create_co_members', [])
    for co_member in co_members:
        share_sum += co_member.active_shares
    selected_subscription = request.session['selectedsubscription',-1]
    total_shares = next(
            iter(SubscriptionTypeDao.get_by_id(selectedsubscription).values_list('shares', flat=True) or []), 1)
    required_shares = max(0,total_shares-max(1,share_sum))        
    
    if request.method == 'POST':
        try:
            share_sum = int(request.POST.get('shares_mainmember'))
            for co_member in co_members:
                share_sum += int(request.POST.get(co_member.email))
            share_error = share_error or share_sum<required_shares   
        except:
            share_error = True      
        if not share_error:
            Subscription = None
            if selected_subscription > -1:
                start_date = request.session['start_date']
                depot = request.session['selecteddepot']            
                subscription = create_subscription(start_date, depot, selected_subscription)
            if member.pk is None:
               create_member(member, subscription)   
            else:
               update_member(member, subscription)
            shares = int(request.POST.get('shares_mainmember'))
            for i in range(shares):
                create_share(member)
            for co_member in co_members:
                shares = int(request.POST.get(co_member.email))
                if co_member.pk is None:
                    create_member(co_member,subscription, member, shares)
                else:
                    update_member(co_member,subscription, member, shares)
                for i in range(shares):
                    create_share(co_member)
            if subscription is not None:
                send_subscription_created_mail(subscription)
            request.session['selected_subscription'] = None
            request.session['selecteddepot'] = None
            request.session['start_date'] = None
            request.session['create_co_members'] = None  
            if request.user.is_authenticated():
                return redirect('/my/subscription')
            else:
                return redirect('/my/welcome')
    renderdict = {      
        'share_error': share_error,
        'total_shares': total_shares,
        'required_shares': required_shares,
        'member': member,
        'co_members': co_members
    }
    return render(request, 'createsubscription/select_shares.html', renderdict)
    

def cs_add_member(request, subscription_id):
    memberexists = False
    memberblocked = False
    co_members = request.session.get('create_co_members', [])
    if request.user.is_authenticated():
        member = request.user.member
    else:
        member = request.session.get('main_member')
    if member is None:
        return redirect('http://'+Config.server_url())
    if request.method == 'POST':
        memberform = RegisterMemberForm(request.POST)
        member = next(iter(MemberDao.members_by_email(request.POST.get('email')) or []), None)
        if member is not None:
            memberexists = True
            memberblocked= member.blocked
        if memberform.is_valid()or (memberexists is True and memberblocked is False):
            if memberexis is False:
                member = Member(**memberform.cleaned_data)
            co_members.append(member)
            request.session['create_co_members'] = co_members
            if request.POST.get('more'):
                redirect('/my/create/subscription/addmembers')
    initial = {'addr_street': member.addr_street,
                   'addr_zipcode': member.addr_zipcode,
                   'addr_location': member.addr_location,
                   'phone': member.phone,
                   }
    memberform = RegisterMemberForm(initial=initial)
    renderdict = {
        'memberexists': memberexists,
        'memberblocked': memberexists,
        'memberform': memberform,
        'member': member,
    }
    return render(request, 'add_member_cs.html', renderdict)


def cs_cancel_create_subscription(request):
    request.session['main_member'] = None
    request.session['selected_subscription'] = None
    request.session['selecteddepot'] = None
    request.session['start_date'] = None
    request.session['create_co_members'] = None    
    if request.user.is_authenticated():
        return redirect('/my/subscription')
    else:
        return redirect('http://'+Config.server_url())

    
