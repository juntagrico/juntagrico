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
from django.conf import settings

import xlsxwriter

from my_ortoloco.models import *
from my_ortoloco.forms import *
from my_ortoloco.helpers import *
from my_ortoloco.filters import Filter
from my_ortoloco.mailer import *
from my_ortoloco.personalisation.personal_utils import enrich_menu_dict

from static_ortoloco.models import StaticContent

import hashlib
from static_ortoloco.models import Politoloco

from decorators import primary_loco_of_abo


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(random.choice(chars) for x in range(size))

def get_menu_dict(request):
    loco = request.user.loco
    next_jobs = []

    def filter_to_past_boehnli(boehnli):
        res = []
        for bohne in boehnli:
            if bohne.job.time.year == date.today().year and bohne.job.time < timezone.now():
                res.append(bohne)
        return res
    abo_size=0
    if loco.abo is not None:
        partner_bohnen = []
        for abo_loco in loco.abo.bezieher_locos():
            if abo_loco == loco: continue
            partner_bohnen.extend(filter_to_past_boehnli(Boehnli.objects.filter(loco=abo_loco)))

        userbohnen = filter_to_past_boehnli(Boehnli.objects.filter(loco=loco))
        abo_size = loco.abo.size * 10

        # amount of beans shown => round up if needed never down
        bohnenrange = range(0, max(userbohnen.__len__(), int(math.ceil(loco.abo.size * 10 / loco.abo.locos.count()))))
        bohnenrange = range(0, max(abo_size, len(userbohnen) + len(partner_bohnen)))

        for bohne in Boehnli.objects.all().filter(loco=loco).order_by("job__time"):
            if bohne.job.time > timezone.now():
                next_jobs.append(bohne.job)
    else:
        bohnenrange = None
        partner_bohnen = []
        userbohnen = []
        next_jobs = []

    depot_admin = Depot.objects.filter(contact=request.user.loco)
    area_admin = Taetigkeitsbereich.objects.filter(coordinator=request.user.loco)
    menu_dict = {
        'user': request.user,
        'bohnenrange': bohnenrange,
        'userbohnen_total': len(userbohnen),
        'userbohnen_kernbereich': len([bohne for bohne in userbohnen if bohne.is_in_kernbereich()]),
        'partner_bohnen_total': len(userbohnen) + len(partner_bohnen),
        'partner_bohnen_kernbereich': len(userbohnen) + len([bohne for bohne in partner_bohnen if bohne.is_in_kernbereich()]),
        'abo_size': abo_size,
        'next_jobs': next_jobs,
        'can_filter_locos': request.user.has_perm('my_ortoloco.can_filter_locos'),
        'can_filter_abos': request.user.has_perm('my_ortoloco.can_filter_abos'),
        'can_send_mails': request.user.has_perm('my_ortoloco.can_send_mails'),
        'operation_group': request.user.has_perm('my_ortoloco.is_operations_group'),
        'depot_admin': depot_admin,
        'area_admin': area_admin,
        'depot_list_url': settings.MEDIA_URL+ settings.MEDIA_ROOT +"/dpl.pdf",
    }
    enrich_menu_dict(request,menu_dict)
    return menu_dict


@login_required
def my_home(request):
    """
    Overview on myortoloco
    """
    announcement = ""
    if StaticContent.objects.all().filter(name='my.ortoloco').__len__() > 0:
        announcement = u"<h3>Ankündigungen:</h3>" + StaticContent.objects.all().filter(name='my.ortoloco')[0].content + "</br>"

    next_jobs = set(get_current_jobs()[:7])
    pinned_jobs = set(Job.objects.filter(pinned=True, time__gte=timezone.now()))
    next_aktionstage = set(RecuringJob.objects.filter(typ__name="Aktionstag", time__gte=timezone.now()).order_by("time")[:2])
    renderdict = get_menu_dict(request)
    renderdict.update({
        'jobs': sorted(next_jobs.union(pinned_jobs).union(next_aktionstage), key=lambda job: job.time),
        'teams': Taetigkeitsbereich.objects.filter(hidden=False).order_by("-core", "name"),
        'no_abo': request.user.loco.abo is None,
        'announcement': announcement
    })

    return render(request, "myhome.html", renderdict)


@login_required
def my_job(request, job_id):
    """
    Details for a job
    """
    loco = request.user.loco
    job = get_object_or_404(Job, id=int(job_id))

    if request.method == 'POST':
        num = request.POST.get("jobs")
        # adding participants
        add = int(num)
        for i in range(add):
            Boehnli.objects.create(loco=loco, job=job)
        # redirect to same page such that refresh in the browser or back
        # button does not trigger a resubmission of the form
        return HttpResponseRedirect('my/jobs')
    
    
    all_participants = Loco.objects.filter(boehnli__job=job)
    number_of_participants = len(all_participants)
    unique_participants = all_participants.annotate(boehnli_for_job=Count('id')).distinct()

    participants_summary = []
    emails = []
    for loco in unique_participants:
        name = u'{} {}'.format(loco.first_name, loco.last_name)
        if loco.boehnli_for_job == 2:
            name = name + u' (mit einer weiteren Person)'
        elif loco.boehnli_for_job > 2:
            name = name + u' (mit {} weiteren Personen)'.format(loco.boehnli_for_job - 1)
        contact_url = u'/my/kontakt/loco/{}/{}/'.format(loco.id, job_id)
        reachable = loco.reachable_by_email==True or request.user.is_staff or job.typ.bereich.coordinator==loco
        participants_summary.append((name, None, contact_url, reachable))
        emails.append(loco.email)
        
        
    slotrange = range(0, job.slots)
    allowed_additional_participants = range(1, job.slots - number_of_participants + 1)
    job_fully_booked = len(allowed_additional_participants) == 0
    job_is_in_past = job.end_time() < timezone.now()
    job_is_running = job.start_time() < timezone.now()
    job_canceled = job.canceled
    can_subscribe = not(job_fully_booked or job_is_in_past or job_is_running or job_canceled)
    
    renderdict = get_menu_dict(request)
    jobendtime = job.end_time()
    renderdict.update({
        'admin': request.user.is_staff or job.typ.bereich.coordinator==loco,
        'emails': "\n".join(emails),
        'number_of_participants': number_of_participants,
        'participants_summary': participants_summary,
        'participants_summary': participants_summary,
        'job': job,
        'slotrange': slotrange,
        'allowed_additional_participants': allowed_additional_participants,
        'job_fully_booked': job_fully_booked,
        'job_is_in_past': job_is_in_past,
        'job_is_running': job_is_running,
        'job_canceled': job_canceled,
        'can_subscribe': can_subscribe
    })
    return render(request, "job.html", renderdict)


@login_required
def my_depot(request, depot_id):
    """
    Details for a Depot
    """
    depot = get_object_or_404(Depot, id=int(depot_id))

    renderdict = get_menu_dict(request)
    renderdict.update({
        'depot': depot
    })
    return render(request, "depot.html", renderdict)


@login_required
def my_participation(request):
    """
    Details for all areas a loco can participate
    """
    loco = request.user.loco
    my_areas = []
    success = False
    if request.method == 'POST':
        old_areas = set(loco.areas.all())
        new_areas = set(area for area in Taetigkeitsbereich.objects.filter(hidden=False)
                        if request.POST.get("area" + str(area.id)))
        if old_areas != new_areas:
            loco.areas = new_areas
            loco.save()
            for area in new_areas - old_areas:
                send_new_loco_in_taetigkeitsbereich_to_bg(area, loco)

        success = True

    for area in Taetigkeitsbereich.objects.filter(hidden=False):
        if area.hidden:
            continue
        my_areas.append({
            'name': area.name,
            'checked': loco in area.locos.all(),
            'id': area.id,
            'core': area.core,
            'coordinator': area.coordinator
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'areas': my_areas,
        'success': success,
        'menu': {'participation': 'active'},
    })
    return render(request, "participation.html", renderdict)


@login_required
def my_pastjobs(request):
    """
    All past jobs of current user
    """
    loco = request.user.loco

    allebohnen = Boehnli.objects.filter(loco=loco)
    past_bohnen = []

    for bohne in allebohnen:
        if bohne.job.time < timezone.now():
            past_bohnen.append(bohne)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'bohnen': past_bohnen,
        'menu': {'participation': 'active'},
    })
    return render(request, "my_pastjobs.html", renderdict)





@login_required
def my_team(request, bereich_id):
    """
    Details for a team
    """

    job_types = JobType.objects.all().filter(bereich=bereich_id)

    otjobs = get_current_one_time_jobs().filter(bereich=bereich_id)
    rjobs = get_current_recuring_jobs().filter(typ__in=job_types)
    
    jobs = list(rjobs)

    if len(otjobs) > 0:
        jobs.extend(list(otjobs))
        jobs.sort(key=lambda job: job.time)



    renderdict = get_menu_dict(request)
    renderdict.update({
        'team': get_object_or_404(Taetigkeitsbereich, id=int(bereich_id)),
        'jobs': jobs,
    })
    return render(request, "team.html", renderdict)


@login_required
def my_einsaetze(request):
    """
    All jobs to be sorted etc.
    """
    renderdict = get_menu_dict(request)

    jobs = get_current_jobs()
    renderdict.update({
        'jobs': jobs,
        'show_all': True,
        'menu': {'jobs': 'active'},
    })

    return render(request, "jobs.html", renderdict)


@login_required
def my_einsaetze_all(request):
    """
    All jobs to be sorted etc.
    """
    renderdict = get_menu_dict(request)
    jobs = Job.objects.all().order_by("time")
    renderdict.update({
        'jobs': jobs,
        'menu': {'jobs': 'active'},
    })

    return render(request, "jobs.html", renderdict)


@login_required
def my_contact(request):
    """
    Kontaktformular
    """
    loco = request.user.loco
    is_sent = False

    if request.method == "POST":
        # send mail to bg
        send_contact_form(request.POST.get("subject"), request.POST.get("message"), loco, request.POST.get("copy"))
        is_sent = True

    renderdict = get_menu_dict(request)
    renderdict.update({
        'usernameAndEmail': loco.first_name + " " + loco.last_name + "<" + loco.email + ">",
        'is_sent': is_sent,
        'menu': {'contact': 'active'},
    })
    return render(request, "my_contact.html", renderdict)

@login_required
def my_contact_loco(request, loco_id, job_id):
    """
    Kontaktformular Locos
    """
    loco = request.user.loco
    contact_loco = get_object_or_404(Loco, id=int(loco_id))#Loco.objects.all().filter(id = loco_id)
    is_sent = False

    if request.method == "POST":
        # send mail to loco
        index = 1
        attachements = []
        while request.FILES.get("image-" + str(index)) is not None:
            attachements.append(request.FILES.get("image-" + str(index)))
            index += 1
        send_contact_loco_form(request.POST.get("subject"), request.POST.get("message"), loco, contact_loco, request.POST.get("copy"),attachements)
        is_sent = True
    job = Job.objects.filter(id=job_id)[0]
    renderdict = get_menu_dict(request)
    renderdict.update({        
        'admin': request.user.is_staff or job.typ.bereich.coordinator==loco,
        'usernameAndEmail': loco.first_name + " " + loco.last_name + "<" + loco.email + ">",
        'loco_id': loco_id,
        'loco_name': contact_loco.first_name + " " + contact_loco.last_name,
        'is_sent': is_sent,
        'job_id': job_id
    })
    return render(request, "my_contact_loco.html", renderdict)


@login_required
def my_profile(request):
    success = False
    loco = request.user.loco
    if request.method == 'POST':
        locoform = ProfileLocoForm(request.POST, instance=loco)
        if locoform.is_valid():
            #set all fields of user
            loco.first_name = locoform.cleaned_data['first_name']
            loco.last_name = locoform.cleaned_data['last_name']
            loco.email = locoform.cleaned_data['email']
            loco.addr_street = locoform.cleaned_data['addr_street']
            loco.addr_zipcode = locoform.cleaned_data['addr_zipcode']
            loco.addr_location = locoform.cleaned_data['addr_location']
            loco.phone = locoform.cleaned_data['phone']
            loco.mobile_phone = locoform.cleaned_data['mobile_phone']
            loco.reachable_by_email = locoform.cleaned_data['reachable_by_email']
            loco.save()
            success = True
    else:
        locoform = ProfileLocoForm(instance=loco)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'locoform': locoform,
        'success': success,
        'menu': {'personalInfo': 'active'},
    })
    return render(request, "profile.html", renderdict)


@login_required
def my_change_password(request):
    success = False
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            success = True
    else:
        form = PasswordForm()

    renderdict = get_menu_dict(request)
    renderdict.update({
        'form': form,
        'success': success
    })
    return render(request, 'password.html', renderdict)


def my_new_password(request):
    sent = False
    if request.method == 'POST':
        sent = True
        locos = Loco.objects.filter(email=request.POST.get('username'))
        if len(locos) > 0:
            loco = locos[0]
            pw = password_generator()
            loco.user.set_password(pw)
            loco.user.save()
            send_mail_password_reset(loco.email, pw, request.META["HTTP_HOST"])

    renderdict = {
        'sent': sent
    }
    return render(request, 'my_newpassword.html', renderdict)


def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/aktuelles")


def mini_migrate_future_zusatzabos(request):
    new_abo_future_extra = []
    Throughclass = Abo.future_extra_abos.through

    abos = Abo.objects.filter(extra_abos_changed=False)
    for abo in abos:
        for extra in abo.extra_abos.all():
            new_abo_future_extra.append(Throughclass(extraabotype=extra, abo=abo))

    Throughclass.objects.bulk_create(new_abo_future_extra)
    abos.update(extra_abos_changed=True)
    return HttpResponse("Done!")


def test_filters(request):
    lst = Filter.get_all()
    res = []
    for name in Filter.get_names():
        res.append("<br><br>%s:" % name)
        tmp = Filter.execute([name], "OR")
        data = Filter.format_data(tmp, unicode)
        res.extend(data)
    return HttpResponse("<br>".join(res))


def test_filters_post(request):
    # TODO: extract filter params from post request
    # the full list of filters is obtained by Filter.get_names()
    filters = ["Zusatzabo Eier", "Depot GZ Oerlikon"]
    op = "AND"
    res = ["Eier AND Oerlikon:<br>"]
    locos = Filter.execute(filters, op)
    data = Filter.format_data(locos, lambda loco: "%s! (email: %s)" % (loco, loco.email))
    res.extend(data)
    return HttpResponse("<br>".join(res))





