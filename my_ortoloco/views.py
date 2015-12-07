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
import xlsxwriter

from my_ortoloco.models import *
from my_ortoloco.forms import *
from my_ortoloco.helpers import *
from my_ortoloco.filters import Filter
from my_ortoloco.mailer import *

from static_ortoloco.models import StaticContent

import hashlib
from static_ortoloco.models import Politoloco

from decorators import primary_loco_of_abo


def password_generator(size=8, chars=string.ascii_uppercase + string.digits): return ''.join(random.choice(chars) for x in range(size))

def get_menu_dict(request):
    loco = request.user.loco
    next_jobs = set()
    if loco.abo is not None:
        allebohnen = Boehnli.objects.filter(loco=loco)
        userbohnen = []

        for bohne in allebohnen:
            if bohne.job.time.year == date.today().year and bohne.job.time < datetime.datetime.now():
                userbohnen.append(bohne)

        # amount of beans shown => round up if needed never down
        bohnenrange = range(0, max(userbohnen.__len__(), int(math.ceil(loco.abo.size * 10 / loco.abo.locos.count()))))

        for bohne in Boehnli.objects.all().filter(loco=loco).order_by("job__time"):
            if bohne.job.time > datetime.datetime.now():
                next_jobs.add(bohne.job)
    else:
        bohnenrange = None
        userbohnen = []
        next_jobs = set()

    depot_admin = Depot.objects.filter(contact=request.user.loco)
    area_admin = Taetigkeitsbereich.objects.filter(coordinator=request.user.loco)
    return {
        'user': request.user,
        'bohnenrange': bohnenrange,
        'userbohnen_total': len(userbohnen),
        'userbohnen_kernbereich': len([bohne for bohne in userbohnen if bohne.is_in_kernbereich()]),
        'next_jobs': next_jobs,
        'staff_user': request.user.is_staff,
        'depot_admin': depot_admin,
        'area_admin': area_admin,
        'politoloco': request.user.has_perm('static_ortoloco.can_send_newsletter')
    }


@login_required
def my_home(request):
    """
    Overview on myortoloco
    """
    announcement = ""
    if StaticContent.objects.all().filter(name='my.ortoloco').__len__() > 0:
        announcement = u"<h3>Ankündigungen:</h3>" + StaticContent.objects.all().filter(name='my.ortoloco')[0].content + "</br>"

    next_jobs = set(get_current_jobs()[:7])
    pinned_jobs = set(Job.objects.filter(pinned=True, time__gte=datetime.datetime.now()))
    next_aktionstage = set(Job.objects.filter(typ__name="Aktionstag", time__gte=datetime.datetime.now()).order_by("time")[:2])
    renderdict = get_menu_dict(request)
    renderdict.update({
        'jobs': sorted(next_jobs.union(pinned_jobs).union(next_aktionstage), key=lambda job: job.time),
        'teams': Taetigkeitsbereich.objects.filter(hidden=False),
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

    participants_dict = defaultdict(int)
    boehnlis = Boehnli.objects.filter(job_id=job.id)
    number_of_participants = len(boehnlis)

    participants_new_dict = defaultdict(dict)
    for boehnli in boehnlis:
        if boehnli.loco is not None:
            loco_info = participants_new_dict[boehnli.loco.first_name + ' ' + boehnli.loco.last_name]
            current_count = loco_info.get("count", 0)
            current_msg = loco_info.get("msg", [])
            loco_info["count"] = current_count + 1
            loco_info["email"] = boehnli.loco.email
            #current_msg.append("boehnli.comment")
            loco_info["msg"] = current_msg
            if boehnli.loco.reachable_by_email==True or request.user.is_staff or job.typ.bereich.coordinator==loco:
                loco_info["url"] = "/my/kontakt/loco/" + str(boehnli.loco.id) + "/" +str(job_id) + "/"
                loco_info["reachable"] = True;
            else:
                loco_info["url"] = ""
                loco_info["reachable"] = False;
    print participants_new_dict

    participants_summary = []
    emails = []
    for loco_name, loco_dict in participants_new_dict.iteritems():
        # print loco_name, loco_dict
        count = loco_dict.get("count")
        msg = loco_dict.get("msg")
        url = loco_dict.get("url")
        reachable = loco_dict.get("reachable")
        emails.append(loco_dict.get("email"))
        # msg = ", ".join(loco_dict.get("msg"))
        if count == 1:
            participants_summary.append((loco_name, None, url, reachable))
        elif count == 2:
            participants_summary.append((loco_name + ' (mit einer weiteren Person)', msg, url, reachable))
        else:
            participants_summary.append((loco_name
                                                    + ' (mit ' + str(count - 1)
                                                    + ' weiteren Personen)', msg, url, reachable))

    # for boehnli in boehnlis:
    #     if boehnli.loco is not None:
    #         participants_dict[boehnli.loco.first_name + ' ' + boehnli.loco.last_name] += 1

    # participants_summary = []
    # for loco_name, number_of_companions in participants_dict.iteritems():
    #     if number_of_companions == 1:
    #         participants_summary.append(loco_name)
    #     elif number_of_companions == 2:
    #         participants_summary.append(loco_name + ' (mit einer weiteren Person)')
    #     else:
    #         participants_summary.append(loco_name
    #                                     + ' (mit ' + str(number_of_companions - 1)
    #                                     + ' weiteren Personen)')

    slotrange = range(0, job.slots)
    allowed_additional_participants = range(1, job.slots - number_of_participants + 1)
    job_fully_booked = len(allowed_additional_participants) == 0
    job_is_in_past = job.end_time() < datetime.datetime.now()
    job_is_running = job.start_time() < datetime.datetime.now()
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
        'success': success
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
        if bohne.job.time < datetime.datetime.now():
            past_bohnen.append(bohne)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'bohnen': past_bohnen
    })
    return render(request, "my_pastjobs.html", renderdict)


@permission_required('static_ortoloco.can_send_newsletter')
def send_politoloco(request):
    """
    Send politoloco newsletter
    """
    sent = 0
    if request.method == 'POST':
        emails = set()
        if request.POST.get("allpolitoloco"):
            for loco in Politoloco.objects.all():
                emails.add(loco.email)

        if request.POST.get("allortolocos"):
            for loco in Loco.objects.all():
                emails.add(loco.email)

        if request.POST.get("allsingleemail"):
            emails.add(request.POST.get("singleemail"))

        index = 1
        attachements = []
        while request.FILES.get("image-" + str(index)) is not None:
            attachements.append(request.FILES.get("image-" + str(index)))
            index += 1

        send_politoloco_mail(request.POST.get("subject"), request.POST.get("message"), request.POST.get("textMessage"), emails, request.META["HTTP_HOST"], attachements)
        sent = len(emails)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'politolocos': Politoloco.objects.count(),
        'ortolocos': Loco.objects.count(),
        'sent': sent
    })
    return render(request, 'mail_sender_politoloco.html', renderdict)


@login_required
def my_abo(request):
    """
    Details for an abo of a loco
    """
    renderdict = get_menu_dict(request)

    if request.user.loco.abo != None:
        current_zusatzabos = request.user.loco.abo.extra_abos.all()
        future_zusatzabos = request.user.loco.abo.future_extra_abos.all()
        zusatzabos_changed = (request.user.loco.abo.extra_abos_changed and
                              set(current_zusatzabos) != set(future_zusatzabos))

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
        'scheine_unpaid': request.user.loco.anteilschein_set.filter(paid=False).count(),
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
        request.user.loco.abo.depot = get_object_or_404(Depot, id=int(request.POST.get("depot")))
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
            if request.POST.get("abo" + str(extra_abo.id)) == str(extra_abo.id):
                request.user.loco.abo.future_extra_abos.add(extra_abo)
                extra_abo.future_extra_abos.add(request.user.loco.abo)
            else:
                request.user.loco.abo.future_extra_abos.remove(extra_abo)
                extra_abo.future_extra_abos.remove(request.user.loco.abo)
            request.user.loco.abo.extra_abos_changed = True
            request.user.loco.abo.save()
            extra_abo.save()

        saved = True

    abos = []
    for abo in ExtraAboType.objects.all():
        if request.user.loco.abo.extra_abos_changed:
            if abo in request.user.loco.abo.future_extra_abos.all():
                abos.append({
                    'id': abo.id,
                    'name': abo.name,
                    'selected': True
                })
            else:
                abos.append({
                    'id': abo.id,
                    'name': abo.name
                })
        else:
            if abo in request.user.loco.abo.extra_abos.all():
                abos.append({
                    'id': abo.id,
                    'name': abo.name,
                    'selected': True
                })
            else:
                abos.append({
                    'id': abo.id,
                    'name': abo.name
                })
    renderdict = get_menu_dict(request)
    renderdict.update({
        'saved': saved,
        'loco': request.user.loco,
        "extras": abos
    })
    return render(request, "my_extra_change.html", renderdict)


@login_required
def my_team(request, bereich_id):
    """
    Details for a team
    """

    job_types = JobType.objects.all().filter(bereich=bereich_id)

    jobs = get_current_jobs().filter(typ=job_types)

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
        'show_all': True
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
    })

    return render(request, "jobs.html", renderdict)


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
        'userexists': userexists
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
                anteilschein = Anteilschein(loco=loco, paid=False)
                anteilschein.save()

            send_been_added_to_abo(loco.email, pw, loco.get_name(), scheine, hashlib.sha1(locoform.cleaned_data['email'] + str(abo_id)).hexdigest(), request.META["HTTP_HOST"])

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
        "depots": Depot.objects.all()
    }
    return render(request, "add_loco.html", renderdict)


@login_required
def my_createabo(request):
    """
    Abo erstellen
    """
    loco = request.user.loco
    scheineerror = False
    if loco.abo is None or loco.abo.size is 1:
        selectedabo = "small"
    elif loco.abo.size is 2:
        selectedabo = "big"
    else:
        selectedabo = "house"

    loco_scheine = 0
    if loco.abo is not None:
        for abo_loco in loco.abo.bezieher_locos().exclude(email=request.user.loco.email):
            loco_scheine += abo_loco.anteilschein_set.all().__len__()

    if request.method == "POST":
        scheine = int(request.POST.get("scheine"))
        selectedabo = request.POST.get("abo")

        scheine += loco_scheine
        min_anzahl_scheine = {"none": 1, "small": 2, "big": 4, "house": 20}.get(request.POST.get("abo"))
        if scheine < min_anzahl_scheine:
            scheineerror = True
        else:
            depot = Depot.objects.all().filter(id=request.POST.get("depot"))[0]
            size = {"none": 0, "small": 1, "big": 2, "house": 10}.get(request.POST.get("abo"))

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
                    anteilschein = Anteilschein(loco=loco, paid=False)
                    anteilschein.save()

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
        "loco": request.user.loco,
        "depots": Depot.objects.all(),
        'selected_depot': selected_depot,
        "selected_abo": selectedabo,
        "scheineerror": scheineerror,
        "mit_locos": mit_locos
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
        'is_sent': is_sent
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
        send_contact_loco_form(request.POST.get("subject"), request.POST.get("message"), loco, contact_loco, request.POST.get("copy"))
        is_sent = True

    renderdict = get_menu_dict(request)
    renderdict.update({
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
        'success': success
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

@staff_member_required
def send_email(request):
    return send_email_intern(request)

@permission_required('my_ortoloco.is_depot_admin')
def send_email_depot(request):
    return send_email_intern(request)

@permission_required('my_ortoloco.is_area_admin')
def send_email_area(request):
    return send_email_intern(request)

def send_email_intern(request):
    sent = 0
    if request.method != 'POST':
        raise Http404
    emails = set()
    sender = request.POST.get("sender")
    if request.POST.get("allabo") == "on":
        for loco in Loco.objects.exclude(abo=None).filter(abo__active=True):
            emails.add(loco.email)
    if request.POST.get("allanteilsschein") == "on":
        for loco in Loco.objects.all():
            if loco.anteilschein_set.count() > 0:
                emails.add(loco.email)
    if request.POST.get("all") == "on":
        for loco in Loco.objects.all():
            emails.add(loco.email)
    if request.POST.get("recipients"):
        recipients = re.split(r"\s*,?\s*", request.POST.get("recipients"))
        for recipient in recipients:
            emails.add(recipient)
    if request.POST.get("allsingleemail"):
        emails |= set(request.POST.get("singleemail").split(' '))

    index = 1
    attachements = []
    while request.FILES.get("image-" + str(index)) is not None:
        attachements.append(request.FILES.get("image-" + str(index)))
        index += 1

    if len(emails) > 0:
        send_filtered_mail(request.POST.get("subject"), request.POST.get("message"), request.POST.get("textMessage"), emails, request.META["HTTP_HOST"], attachements, sender=sender)
        sent = len(emails)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'sent': sent
    })
    return render(request, 'mail_sender_result.html', renderdict)


@staff_member_required
def my_mails(request, enhanced=None):
    return my_mails_intern(request, enhanced)

@permission_required('my_ortoloco.is_depot_admin')
def my_mails_depot(request):
    return my_mails_intern(request, "depot")

@permission_required('my_ortoloco.is_area_admin')
def my_mails_area(request):
    return my_mails_intern(request, "area")

def my_mails_intern(request, enhanced, error_message=None):
    renderdict = get_menu_dict(request)
    renderdict.update({
        'recipient_type': request.POST.get("recipient_type"),
        'recipient_type_detail': request.POST.get("recipient_type_detail"),
        'recipients': request.POST.get("recipients"),
        'recipients_count': int(request.POST.get("recipients_count") or 0),
        'filter_value': request.POST.get("filter_value"),
        'mail_subject': request.POST.get("subject"),
        'mail_message': request.POST.get("message"),
        'enhanced': enhanced,
        'email': request.user.loco.email,
        'error_message': error_message
    })
    return render(request, 'mail_sender.html', renderdict)

def current_year_boehlis():
    now = datetime.date.today()
    return Boehnli.objects.filter(job__time__year=now.year, job__time__lt=now)


def current_year_boehnlis_per_loco():
    boehnlis = current_year_boehlis()
    boehnlis_per_loco = defaultdict(int)
    for boehnli in boehnlis:
        boehnlis_per_loco[boehnli.loco] += 1
    return boehnlis_per_loco

def current_year_kernbereich_boehnlis_per_loco():
    boehnlis = current_year_boehlis()
    boehnlis_per_loco = defaultdict(int)
    for boehnli in boehnlis:
        if boehnli.is_in_kernbereich():
            boehnlis_per_loco[boehnli.loco] += 1
    return boehnlis_per_loco


@staff_member_required
def my_filters(request):
    locos = Loco.objects.all()
    boehnlis = current_year_boehnlis_per_loco()
    boehnlis_kernbereich = current_year_kernbereich_boehnlis_per_loco()
    for loco in locos:
        loco.boehnlis = boehnlis[loco]
        loco.boehnlis_kernbereich = boehnlis_kernbereich[loco]

    renderdict = get_menu_dict(request)
    renderdict.update({
        'locos': locos
    })
    return render(request, 'filters.html', renderdict)



@permission_required('my_ortoloco.is_depot_admin')
def my_filters_depot(request, depot_id):
    depot = get_object_or_404(Depot, id=int(depot_id))
    locos = get_locos_for_depot(depot)
    boehnlis = current_year_boehnlis_per_loco()
    boehnlis_kernbereich = current_year_kernbereich_boehnlis_per_loco()
    for loco in locos:
        loco.boehnlis = boehnlis[loco]
        loco.boehnlis_kernbereich = boehnlis_kernbereich[loco]

    renderdict = get_menu_dict(request)
    renderdict.update({
        'locos': locos,
        'enhanced': "depot"
    })
    return render(request, 'filters.html', renderdict)

def get_locos_for_depot(depot):
    abos = Abo.objects.filter(depot = depot)
    res = []
    for a in abos:
        locos = Loco.objects.filter(abo = a)
        for loco in locos:
            res.append(loco)
    return res

@permission_required('my_ortoloco.is_area_admin')
def my_filters_area(request, area_id):
    area = get_object_or_404(Taetigkeitsbereich, id=int(area_id))
    locos = area.locos.all()
    boehnlis = current_year_boehnlis_per_loco()
    boehnlis_kernbereich = current_year_kernbereich_boehnlis_per_loco()
    for loco in locos:
        loco.boehnlis = boehnlis[loco]
        loco.boehnlis_kernbereich = boehnlis_kernbereich[loco]

    renderdict = get_menu_dict(request)
    renderdict.update({
        'locos': locos,
        'enhanced': "area"
    })
    return render(request, 'filters.html', renderdict)


@staff_member_required
def my_abos(request):
    boehnli_map = current_year_boehnlis_per_loco()
    boehnlis_kernbereich_map = current_year_kernbereich_boehnlis_per_loco()
    abos = []
    for abo in Abo.objects.filter():
        boehnlis = 0
        boehnlis_kernbereich = 0
        for loco in abo.bezieher_locos():
            boehnlis += boehnli_map[loco]
            boehnlis_kernbereich += boehnlis_kernbereich_map[loco]

        abos.append({
            'abo': abo,
            'text': get_status_bean_text(100 / (abo.size * 10) * boehnlis if abo.size > 0 else 0),
            'boehnlis': boehnlis,
            'boehnlis_kernbereich': boehnlis_kernbereich,
            'icon': helpers.get_status_bean(100 / (abo.size * 10) * boehnlis if abo.size > 0 else 0)
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'abos': abos
    })

    return render(request, 'abos.html', renderdict)


@permission_required('my_ortoloco.is_depot_admin')
def my_abos_depot(request, depot_id):
    boehnli_map = current_year_boehnlis_per_loco()
    boehnlis_kernbereich_map = current_year_kernbereich_boehnlis_per_loco()
    abos = []
    depot = get_object_or_404(Depot, id=int(depot_id))
    for abo in Abo.objects.filter(depot = depot):
        boehnlis = 0
        boehnlis_kernbereich = 0
        for loco in abo.bezieher_locos():
            boehnlis += boehnli_map[loco]
            boehnlis_kernbereich += boehnlis_kernbereich_map[loco]

        abos.append({
            'abo': abo,
            'text': get_status_bean_text(100 / (abo.size * 10) * boehnlis if abo.size > 0 else 0),
            'boehnlis': boehnlis,
            'boehnlis_kernbereich': boehnlis_kernbereich,
            'icon': helpers.get_status_bean(100 / (abo.size * 10) * boehnlis if abo.size > 0 else 0)
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'abos': abos
    })

    return render(request, 'abos.html', renderdict)


@staff_member_required
def my_depotlisten(request):
    return alldepots_list(request, "")


def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/aktuelles")


def alldepots_list(request, name):
    """
    Printable list of all depots to check on get gemüse
    """
    if name == "":
        depots = Depot.objects.all().order_by("code")
    else:
        depots = [get_object_or_404(Depot, code__iexact=name)]

    overview = {
        'Dienstag': {
            'small_abo': 0,
            'big_abo': 0,
            'entities': 0,
            'egg4': 0,
            'egg6': 0,
            'cheesefull': 0,
            'cheesehalf': 0,
            'cheesequarter': 0,
            'bigobst': 0,
            'smallobst': 0
        },
        'Donnerstag': {
            'small_abo': 0,
            'big_abo': 0,
            'entities': 0,
            'egg4': 0,
            'egg6': 0,
            'cheesefull': 0,
            'cheesehalf': 0,
            'cheesequarter': 0,
            'bigobst': 0,
            'smallobst': 0
        },
        'all': {
            'small_abo': 0,
            'big_abo': 0,
            'entities': 0,
            'egg4': 0,
            'egg6': 0,
            'cheesefull': 0,
            'cheesehalf': 0,
            'cheesequarter': 0,
            'bigobst': 0,
            'smallobst': 0
        }
    }

    for depot in depots:
        row = overview.get(depot.get_weekday_display())
        all = overview.get('all')
        actives = depot.active_abos()
        row['small_abo'] += depot.small_abos(actives)
        row['big_abo'] += depot.big_abos(actives)
        row['entities'] += 2 * depot.big_abos(actives) + depot.small_abos(actives)
        row['egg4'] += depot.vier_eier(actives)
        row['egg6'] += depot.sechs_eier(actives)
        row['cheesefull'] += depot.kaese_ganz(actives)
        row['cheesehalf'] += depot.kaese_halb(actives)
        row['cheesequarter'] += depot.kaese_viertel(actives)
        row['bigobst'] += depot.big_obst(actives)
        row['smallobst'] += depot.small_obst(actives)
        all['small_abo'] += depot.small_abos(actives)
        all['big_abo'] += depot.big_abos(actives)
        all['entities'] += 2 * depot.big_abos(actives) + depot.small_abos(actives)
        all['egg4'] += depot.vier_eier(actives)
        all['egg6'] += depot.sechs_eier(actives)
        all['cheesefull'] += depot.kaese_ganz(actives)
        all['cheesehalf'] += depot.kaese_halb(actives)
        all['cheesequarter'] += depot.kaese_viertel(actives)
        all['bigobst'] += depot.big_obst(actives)
        all['smallobst'] += depot.small_obst(actives)

    renderdict = {
        "overview": overview,
        "depots": depots,
        "datum": datetime.datetime.now()
    }

    return render_to_pdf(request, "exports/all_depots.html", renderdict, 'Depotlisten')


def my_createlocoforsuperuserifnotexist(request):
    """
    just a helper to create a loco for superuser
    """
    if request.user.is_superuser:
        signals.post_save.disconnect(Loco.create, sender=Loco)
        loco = Loco.objects.create(user=request.user, first_name="super", last_name="duper", email=request.user.email, addr_street="superstreet", addr_zipcode="8000",
                                   addr_location="SuperCity", phone="012345678")
        loco.save()
        request.user.loco = loco
        request.user.save()
        signals.post_save.connect(Loco.create, sender=Loco)


    # we do just nothing if its not a superuser or he has already a loco
    return redirect("/my/home")


@staff_member_required
def my_future(request):
    renderdict = get_menu_dict(request)

    small_abos = 0
    big_abos = 0
    house_abos = 0
    small_abos_future = 0
    big_abos_future = 0
    house_abos_future = 0

    extra_abos = dict({})
    for extra_abo in ExtraAboType.objects.all():
        extra_abos[extra_abo.id] = {
            'name': extra_abo.name,
            'future': 0,
            'now': str(extra_abo.extra_abos.count())
        }

    for abo in Abo.objects.all():
        small_abos += abo.size % 2
        big_abos += int(abo.size % 10 / 2)
        house_abos += int(abo.size / 10)
        small_abos_future += abo.future_size % 2
        big_abos_future += int(abo.future_size % 10 / 2)
        house_abos_future += int(abo.future_size / 10)

        if abo.extra_abos_changed:
            for users_abo in abo.future_extra_abos.all():
                extra_abos[users_abo.id]['future'] += 1
        else:
            for users_abo in abo.extra_abos.all():
                extra_abos[users_abo.id]['future'] += 1

    month = int(time.strftime("%m"))
    day = int(time.strftime("%d"))

    renderdict.update({
        'changed': request.GET.get("changed"),
        'big_abos': big_abos,
        'house_abos': house_abos,
        'small_abos': small_abos,
        'big_abos_future': big_abos_future,
        'house_abos_future': house_abos_future,
        'small_abos_future': small_abos_future,
        'extras': extra_abos.itervalues(),
        'abo_change_enabled': month is 12 or (month is 1 and day <= 6)
    })
    return render(request, 'future.html', renderdict)


@staff_member_required
def my_switch_extras(request):
    renderdict = get_menu_dict(request)

    for abo in Abo.objects.all():
        if abo.extra_abos_changed:
            abo.extra_abos = []
            for extra in abo.future_extra_abos.all():
                abo.extra_abos.add(extra)

            abo.extra_abos_changed = False
            abo.save()


    renderdict.update({
    })

    return redirect('/my/zukunft?changed=true')

@staff_member_required
def my_switch_abos(request):
    renderdict = get_menu_dict(request)

    for abo in Abo.objects.all():
        if abo.size is not abo.future_size:
            if abo.future_size is 0:
                abo.active = False
            if abo.size is 0:
                abo.active = True
            abo.size = abo.future_size
            abo.save()


    renderdict.update({
    })

    return redirect('/my/zukunft?changed=true')


@staff_member_required
def my_excel_export(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet("Locos")
    
    worksheet_s.write_string(0, 0, unicode("Name", "utf-8"))
    worksheet_s.write_string(0, 1, unicode("Boehnlis", "utf-8"))
    worksheet_s.write_string(0, 2, unicode("Boehnlis Kernbereich", "utf-8"))
    worksheet_s.write_string(0, 3, unicode("Taetigkeitsbereiche", "utf-8"))
    worksheet_s.write_string(0, 4, unicode("Depot", "utf-8"))
    worksheet_s.write_string(0, 5, unicode("Email", "utf-8"))
    worksheet_s.write_string(0, 6, unicode("Telefon", "utf-8"))
    worksheet_s.write_string(0, 7, unicode("Mobile", "utf-8"))
    
    locos = Loco.objects.all()
    boehnlis = current_year_boehnlis_per_loco()
    boehnlis_kernbereich = current_year_kernbereich_boehnlis_per_loco()
    row = 1
    for loco in locos:
        loco.boehnlis = boehnlis[loco]
        loco.boehnlis_kernbereich = boehnlis_kernbereich[loco]
        loco.bereiche = ""
        for bereich in loco.areas.all():
            loco.bereiche = loco.bereiche + bereich.name +" "
        if loco.bereiche == "":
            loco.bereiche = unicode("-Kein Tätigkeitsbereich-", "utf-8")
        
        loco.depot_name = unicode("Kein Depot definiert", "utf-8")
        if loco.abo is not None:
            loco.depot_name=loco.abo.depot.name
        looco_full_name = loco.first_name + " " + loco.last_name
        worksheet_s.write_string(row, 0, looco_full_name)
        worksheet_s.write(row, 1, loco.boehnlis)
        worksheet_s.write(row, 2, loco.boehnlis_kernbereich)
        worksheet_s.write_string(row, 3, loco.bereiche)
        worksheet_s.write_string(row, 4, loco.depot_name)
        worksheet_s.write_string(row, 5, loco.email)
        worksheet_s.write_string(row, 6, loco.phone)
        if loco.mobile_phone is not None: 
            worksheet_s.write_string(row, 7, loco.mobile_phone)
        row = row + 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response

@staff_member_required
def my_startmigration(request):
    f = StringIO()
    with Swapstd(f):
        call_command('clean_db')
        call_command('import_old_db', request.GET.get("username"), request.GET.get("password"))
    return HttpResponse(f.getvalue(), content_type="text/plain")


@staff_member_required
def migrate_apps(request):
    f = StringIO()
    with Swapstd(f):
        call_command('migrate', 'my_ortoloco')
        call_command('migrate', 'static_ortoloco')
    return HttpResponse(f.getvalue(), content_type="text/plain")


@staff_member_required
def pip_install(request):
    command = "pip install -r requirements.txt"
    res = run_in_shell(request, command)
    return res


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




