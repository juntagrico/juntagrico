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

@login_required
def my_home(request):
    """
    Overview on myortoloco
    """
    next_jobs = Job.objects.all()[0:7]
    teams = Taetigkeitsbereich.objects.all()

    if request.user.loco.abo is not None:
        bohnenrange = range(0, request.user.loco.abo.groesse * 10 / request.user.loco.abo.locos.count())
        allebohnen = Boehnli.objects.filter(loco=request.user.loco)
        userbohnen = []
        for bohne in allebohnen:
            if bohne.job.time.year == date.today().year:
                userbohnen.append(bohne)
        no_abo = False
    else:
        no_abo = True
        bohnenrange = None
        userbohnen = []

    return render(request, "myhome.html", {
        'jobs': next_jobs,
        'teams': teams,
        #abo gesamtbohnen / # bezieher
        'no_abo': no_abo,
        'bohnenrange': bohnenrange,
        'userbohnen': userbohnen.__len__()
    })


@login_required
def my_job(request, job_id):
    """
    Details for a job
    """
    job = get_object_or_404(Job, id=int(job_id))

    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    error = None
    if request.method == 'POST':
        num = request.POST.get("jobs")
        my_bohnen = job.boehnli_set.all().filter(loco=request.user.loco)
        left_bohnen = job.boehnli_set.all().filter(loco=None)
        print left_bohnen.__len__()
        if check_int(num) and 0 < int(num) <= left_bohnen.__len__():
            # adding participants
            add = int(num)
            for bohne in left_bohnen:
                if (add > 0):
                    bohne.loco = request.user.loco
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
            participants.append(bohne.loco.user)
    return render(request, "job.html", {
        'participants': participants,
        'job': job,
        'slotrange': range(0, job.slots),
        'error': error
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
    if Abo.objects.filter(primary_loco=request.user).count() > 0:
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

        return render(request, "my_abo.html", {
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
    else:
        return render(request, "my_abo.html", {
            'noabo': True
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
    print "my"

    if request.method == "POST":
        #  FIXME change to info@ortoloco.ch
        send_mail('Anfrage per my.ortoloco', request.POST.get("message"), request.user.email, ['oliver.ganz@gmail.com'], fail_silently=False)

    renderdict = {
        'usernameAndEmail': request.user.first_name + " " + request.user.last_name + "<" + request.user.email + ">"
    }

    return render(request, "my_contact.html", renderdict)


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
        locos = sorted(loco.user.username for loco in locos)
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
        res.append("<br><br>%s:" %name)
        tmp = Filter.execute([name], "OR")
        data = Filter.format_data(tmp, lambda loco: loco.user.username)
        res.extend(data)
    return HttpResponse("<br>".join(res))


def test_filters_post(request):
    # TODO: extract filter params from post request
    # the full list of filters is obtained by Filter.get_names()

    filters = ["Staff", "Depot GZ Oerlikon"]
    op = "OR"

    res = ["Staff OR Oerlikon:<br>"]
    locos = Filter.execute(filters, op)
    data = Filter.format_data(locos, lambda loco: "%s! (email: %s)" %(loco.user.username, loco.user.email))

    res.extend(data)
    return HttpResponse("<br>".join(res))



