from collections import defaultdict, Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from my_ortoloco.models import *
from my_ortoloco.forms import *
from django.core.mail import send_mail


@login_required
def my_home(request):
    """
    Overview on myortoloco
    """
    next_jobs = Job.objects.all()[0:7]
    teams = Taetigkeitsbereich.objects.all()

    return render(request, "myhome.html", {
        'jobs': next_jobs,
        'teams': teams
    })


@login_required
def my_job(request, job_id):
    """
    Details for a job
    """
    return render(request, "job.html", {
        'job': get_object_or_404(Job, id=int(job_id))
    })


@login_required
def my_participation(request):
    """
    Details for all areas a loco can participate
    """
    my_areas = []
    success = False
    if request.method == 'POST':
        for area in Taetigkeitsbereich.objects.all():
            if request.POST.get("area" + str(area.id)):
                area.users.add(request.user)
                area.save()
            else:
                area.users.remove(request.user)
                area.save()
        success = True

    for area in Taetigkeitsbereich.objects.all():
        my_areas.append({
            'name': area.name,
            'checked': area.users.all().__contains__(request.user),
            'id': area.id,
            'core': area.core,
            'admin': area.coordinator.email
        })

    return render(request, "participation.html", {
        'areas': my_areas,
        'success': success
    })


@login_required
def my_abo(request):
    """
    Details for an abo of a loco
    """
    myabo = Abo.objects.get(primary_loco=request.user)

    if request.method == 'POST':
        aboform = AboForm(request.POST)
        if aboform.is_valid():
            a_unpaid = int(aboform.data['anteilsscheine_added'])
            a_paid = int(aboform.data['anteilsscheine'])
            # neue anteilsscheine loeschen (nur unbezahlte) falls neu weniger
            if request.user.anteilschein_set.count() > a_unpaid + a_paid:
                todelete = request.user.anteilschein_set.count() - (a_unpaid + a_paid)
                for unpaid in request.user.anteilschein_set.all().filter(paid=False):
                    if todelete > 0:
                        unpaid.delete()
                        todelete -= 1

            #neue unbezahlte anteilsscheine hinzufuegen falls erwuenscht
            if request.user.anteilschein_set.count() < a_unpaid + a_paid:
                toadd = (a_unpaid + a_paid) - request.user.anteilschein_set.count()
                for num in range(0, toadd):
                    anteilsschein = Anteilschein(user=request.user, paid=False)
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

    return render(request, "abo.html", {
        'aboform': aboform,
        'zusatzabos': zusatzabos,
        'depots': depots,
        'sharees': myabo.locos.exclude(id=request.user.id),
        'haus_abos': myabo.haus_abos(),
        'grosse_abos': myabo.grosse_abos(),
        'kleine_abos': myabo.kleine_abos(),
        'anteilsscheine_paid': request.user.anteilschein_set.all().filter(paid=True).count(),
        'anteilsscheine_unpaid': request.user.anteilschein_set.all().filter(paid=False).count()
    })


@login_required
def my_team(request, bereich_id):
    """
    Details for a team
    """

    job_types = JobTyp.objects.all().filter(bereich=bereich_id)

    jobs = Job.objects.all().filter(typ=job_types)

    renderdict = {
        'team': get_object_or_404(Taetigkeitsbereich, id=int(bereich_id)),
        'jobs': jobs,
    }

    return render(request, "team.html", renderdict)


@login_required
def my_contact(request):
    """
    Kontaktformular
    """

    if request.method == "POST":
        #  FIXME change to info@ortoloco.ch
        send_mail('Anfrage per my.ortoloco', request.POST.get("message"), request.user.email, ['oliver.ganz@gmail.com'], fail_silently=False)

    renderdict = {
        'usernameAndEmail': request.user.first_name + " " + request.user.last_name + "<" + request.user.email + ">"
    }

    return render(request, "contact.html", renderdict)


@login_required
def my_profile(request):
    success = False
    loco = Loco.objects.get(user=request.user)
    if request.method == 'POST':
        locoform = ProfileLocoForm(request.POST)
        userform = ProfileUserForm(request.POST)
        if locoform.is_valid() and userform.is_valid():
            #set all fields of user
            request.user.first_name = userform.cleaned_data['first_name']
            request.user.last_name = userform.cleaned_data['last_name']
            request.user.email = userform.cleaned_data['email']
            request.user.save()

            loco.addr_street = locoform.cleaned_data['addr_street']
            loco.addr_zipcode = locoform.cleaned_data['addr_zipcode']
            loco.addr_location = locoform.cleaned_data['addr_location']
            loco.phone = locoform.cleaned_data['phone']
            loco.mobile_phone = locoform.cleaned_data['mobile_phone']
            loco.save()

            success = True
    else:
        locoform = ProfileLocoForm(instance=loco)
        userform = ProfileUserForm(instance=request.user)

    renderdict = {
        'locoform': locoform,
        'userform': userform,
        'success': success
    }
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

    return render(request, 'password.html', {
        'form': form,
        'success': success
    })


def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/aktuelles")


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

    # TODO: use name__iexact

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
    
