from collections import defaultdict, Counter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from my_ortoloco.models import *
from my_ortoloco.forms import *


@login_required
def my_home(request):
    """
    Overview on myortoloco
    """

    next_jobs = Job.objects.all()[0:7]
    teams = Taetigkeitsbereich.objects.all()

    renderdict = {
        'jobs': next_jobs,
        'teams': teams
    }

    return render(request, "myhome.html", renderdict)


@login_required
def my_job(request, job_id):
    """
    Details for a job
    """
    print "gags"

    renderdict = {
        'job': get_object_or_404(Job, id=int(job_id))
    }

    return render(request, "job.html", renderdict)


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
def my_profile(request):
    print "susle"
    if (request.method == 'POST'):
        print "post"
        #formset = UserFormSet(request.POST, queryset=User.objects.filter(id=request.user.id))
        #if formset.is_valid():
        #    formset.save()
    else:
        print "other" + request.method
        #user = User.objects.get(id=request.user.id)
        #form = ProfileForm(instance=user)

    renderdict = {
        #'formset': form
    }
    return render(request, "personal_info.html", renderdict)


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
        form = PasswordForm()  # An unbound form

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
    
