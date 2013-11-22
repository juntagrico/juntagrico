# -*- coding: utf-8 -*-
from collections import defaultdict, Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from datetime import date

from my_ortoloco.models import *
from my_ortoloco.forms import *
from my_ortoloco.helpers import render_to_pdf
from my_ortoloco.filters import Filter


def getBohnenDict(request):
    loco = request.user.loco
    if loco.abo is not None:
        allebohnen = Boehnli.objects.filter(loco=loco)
        userbohnen = []
        for bohne in allebohnen:
            if bohne.job.time.year == date.today().year:
                userbohnen.append(bohne)
        bohnenrange = range(0, max(userbohnen.__len__(), loco.abo.groesse * 10 / loco.abo.locos.count()))

    else:
        bohnenrange = None
        userbohnen = []
    return {
        'bohnenrange': bohnenrange,
        'userbohnen': userbohnen.__len__()
    }


@login_required
def my_home(request):
    """
    Overview on myortoloco
    """
    loco = request.user.loco
    next_jobs = Job.objects.all()[0:7]
    teams = Taetigkeitsbereich.objects.all()

    if loco.abo is not None:
        no_abo = False
    else:
        no_abo = True

    jobs = []
    for job in next_jobs:
        jobs.append({
            'time': job.time,
            'id': job.id,
            'typ': job.typ,
            'status': job.get_status_bohne()
        })

    renderdict = getBohnenDict(request)
    renderdict.update({
        'jobs': jobs,
        'teams': teams,
        'no_abo': no_abo
    })

    return render(request, "myhome.html", renderdict)


@login_required
def my_job(request, job_id):
    """
    Details for a job
    """
    loco = request.user.loco
    job = get_object_or_404(Job, id=int(job_id))

    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    error = None
    if request.method == 'POST':
        num = request.POST.get("jobs")
        my_bohnen = job.boehnli_set.all().filter(loco=loco)
        left_bohnen = job.boehnli_set.all().filter(loco=None)
        if check_int(num) and 0 < int(num) <= left_bohnen.__len__():
            # adding participants
            add = int(num)
            for bohne in left_bohnen:
                if (add > 0):
                    bohne.loco = loco
                    bohne.save()
                    add -= 1
        elif check_int(num) and int(num) < 0 and my_bohnen.__len__() >= -int(num):
            # remove some participants
            remove = -int(num)
            for bohne in my_bohnen:
                if remove > 0:
                    bohne.loco = None
                    bohne.save()
                    remove -= 1
        else:
            error = "Ungueltige Anzahl Einschreibungen"

    boehnlis = Boehnli.objects.filter(job_id=job.id)
    participants = []
    for bohne in boehnlis:
        if bohne.loco is not None:
            participants.append(bohne.loco)

    renderdict = getBohnenDict(request)
    renderdict.update({
        'participants': participants,
        'job': job,
        'slotrange': range(0, job.slots),
        'error': error
    });
    return render(request, "job.html", renderdict)


@login_required
def my_participation(request):
    """
    Details for all areas a loco can participate
    """
    loco = request.user.loco
    my_areas = []
    success = False
    if request.method == 'POST':
        for area in Taetigkeitsbereich.objects.all():
            if request.POST.get("area" + str(area.id)):
                if loco not in area.locos.all():
                    area.locos.add(loco)
                    send_mail('Neues Mitglied im Taetigkeitsbereich ' + area.name, 'Soeben hat sich ' + loco.first_name + " " + loco.last_name + ' in den Taetigkeitsbereich ' + area.name + ' eingetragen', 'orto@xiala.net', [area.coordinator.email], fail_silently=False)
                    area.save()
            else:
                area.locos.remove(loco)
                area.save()
        success = True

    for area in Taetigkeitsbereich.objects.all():
        my_areas.append({
            'name': area.name,
            'checked': area.locos.all().__contains__(loco),
            'id': area.id,
            'core': area.core,
            'admin': area.coordinator.email
        })

    renderdict = getBohnenDict(request)
    renderdict.update({
        'areas': my_areas,
        'success': success
    })
    return render(request, "participation.html", renderdict)


@login_required
def my_abo(request):
    """
    Details for an abo of a loco
    """
    loco = request.user.loco
    if Abo.objects.filter(primary_loco=loco).count() > 0:
        myabo = Abo.objects.get(primary_loco=loco)

        if request.method == 'POST':
            aboform = AboForm(request.POST)
            if aboform.is_valid():
                a_unpaid = int(aboform.data['anteilsscheine_added'])
                a_paid = int(aboform.data['anteilsscheine'])
                # neue anteilsscheine loeschen (nur unbezahlte) falls neu weniger
                if loco.anteilschein_set.count() > a_unpaid + a_paid:
                    todelete = loco.anteilschein_set.count() - (a_unpaid + a_paid)
                    for unpaid in loco.anteilschein_set.all().filter(paid=False):
                        if todelete > 0:
                            unpaid.delete()
                            todelete -= 1

                #neue unbezahlte anteilsscheine hinzufuegen falls erwuenscht
                if loco.anteilschein_set.count() < a_unpaid + a_paid:
                    toadd = (a_unpaid + a_paid) - loco.anteilschein_set.count()
                    for num in range(0, toadd):
                        anteilsschein = Anteilschein(locor=loco, paid=False)
                        anteilsschein.save()

                # abo groesse setzen
                abosize = int(aboform.data['kleine_abos']) + 2 * int(aboform.data['grosse_abos']) + 10 * int(aboform.data['haus_abos'])
                if abosize != myabo.groesse:
                    myabo.groesse = abosize
                    myabo.save()

                # depot wechseln
                if myabo.depot.id != aboform.data['depot']:
                    myabo.depot = Depot.objects.get(id=aboform.data['depot'])
                    myabo.save()

                # zusatzabos
                for zusatzabo in ExtraAboType.objects.all():
                    if aboform.data.has_key('abo' + str(zusatzabo.id)):
                        myabo.extra_abos.add(zusatzabo)
                        myabo.save()
                    else:
                        myabo.extra_abos.remove(zusatzabo)
                        myabo.save()

        aboform = AboForm()
        depots = []
        for depot in Depot.objects.all():
            depots.append({
                'id': depot.id,
                'name': depot.name,
                'selected': myabo.depot == depot
            })

        zusatzabos = []
        for abo in ExtraAboType.objects.all():
            zusatzabos.append({
                'name': abo.name,
                'id': abo.id,
                'checked': myabo.extra_abos.all().__contains__(abo)
            })

        renderdict = getBohnenDict(request)
        renderdict.update({
            'aboform': aboform,
            'zusatzabos': zusatzabos,
            'depots': depots,
            'sharees': myabo.locos.exclude(id=loco.id),
            'haus_abos': myabo.haus_abos(),
            'grosse_abos': myabo.grosse_abos(),
            'kleine_abos': myabo.kleine_abos(),
            'anteilsscheine_paid': loco.anteilschein_set.all().filter(paid=True).count(),
            'anteilsscheine_unpaid': loco.anteilschein_set.all().filter(paid=False).count()
        })
        return render(request, "my_abo.html", renderdict)
    else:
        renderdict = getBohnenDict(request)
        renderdict.update({
            'noabo': True
        })
        return render(request, "my_abo.html", renderdict)


@login_required
def my_team(request, bereich_id):
    """
    Details for a team
    """

    job_types = JobTyp.objects.all().filter(bereich=bereich_id)

    jobs = Job.objects.all().filter(typ=job_types)

    renderdict = getBohnenDict(request)
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
    renderdict = getBohnenDict(request)
    renderdict.update({
        'jobs': Job.objects.all()
    })

    return render(request, "jobs.html", renderdict)


@login_required
def my_contact(request):
    """
    Kontaktformular
    """
    loco = request.user.loco

    if request.method == "POST":
        send_mail('Anfrage per my.ortoloco', request.POST.get("message"), loco.email, ['orto@xiala.net'], fail_silently=False)

    renderdict = getBohnenDict(request)
    renderdict.update({
        'usernameAndEmail': loco.first_name + " " + loco.last_name + "<" + loco.email + ">"
    })
    return render(request, "my_contact.html", renderdict)


@login_required
def my_profile(request):
    success = False
    loco = request.user.loco
    if request.method == 'POST':
        locoform = ProfileLocoForm(request.POST)
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
            loco.save()

            success = True
    else:
        locoform = ProfileLocoForm(instance=loco)

    renderdict = getBohnenDict(request)
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

    renderdict = getBohnenDict(request)
    renderdict.update({
        'form': form,
        'success': success
    })
    return render(request, 'password.html', renderdict)


def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/aktuelles")


def depot_list(request, name):
    """
    Create table of users and their abos for a specific depot.
    """
    depot = get_object_or_404(Depot, code=name)

    # get all abos of this depot
    abos = Abo.objects.filter(depot=depot)

    # helper function to format set of locos consistently
    def locos_to_str(locos):
        # TODO: use first and last name
        locos = sorted(unicode(loco) for loco in locos)
        return u", ".join(locos)

    # build rows of data.
    abotypes = ExtraAboType.objects.all()
    header = ["Abo id", "Personen", u"Groesse"]
    header.extend(i.name for i in abotypes)
    header.append("abgeholt")
    data = []
    for abo in abos:
        extra_abos = set(abo.extra_abos.all())
        row = [str(abo.id), locos_to_str(abo.locos.all()), str(abo.groesse)]
        row.extend("1" if i in extra_abos else "" for i in abotypes)
        row.append("")
        data.append(row)

    renderdict = {
        "depot": depot,
        "table_header": header,
        "table_data": data,
    }

    return render_to_pdf(request, "depot_pdf.html", renderdict)


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
    data = Filter.format_data(locos, lambda loco: "%s! (email: %s)" %(loco, loco.email))
    res.extend(data)
    return HttpResponse("<br>".join(res))



