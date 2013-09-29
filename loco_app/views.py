from collections import defaultdict, Counter

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.forms.models import modelformset_factory
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.forms import ModelForm

from django.forms import ModelForm

from loco_app.models import *
import os
import time, json, base64, hmac, sha, urllib
from django.utils import simplejson


def home(request):
    """
    Homepage of "static" page
    """

    renderdict = {
        'submenu': get_object_or_404(StaticContent, name='HomeUnterMenu'),
        #'homeTitel': get_object_or_404(StaticContent, name='HomeTitel'),
        #'homeText': get_object_or_404(StaticContent, name='HomeText'),
        'menu': {
            'home': 'active'
        }
    }

    return render(request, "web/home.html", renderdict)


def about(request):
    """
    About ortoloco of "static" page
    """

    renderdict = {
        'menu': {
            'about': 'active',
            'aboutChild': 'active'
        }
    }

    return render(request, "web/about.html", renderdict)


def portrait(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'portrait': 'active'
        }
    }

    return render(request, "web/portrait.html", renderdict)


def background(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'background': 'active'
        }
    }

    return render(request, "web/background.html", renderdict)


def abo(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'abo': 'active'
        }
    }

    return render(request, "web/abo.html", renderdict)


def faq(request):
    """
    FAQ ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'about': 'active',
            'faq': 'active'
        }
    }

    return render(request, "web/faq.html", renderdict)


def join(request):
    """
    About ortoloco of "static" page
    """
    renderdict = {
        'menu': {
            'join': 'active'
        }
    }

    return render(request, "web/join.html", renderdict)


def media(request):
    """
    About ortoloco of "static" page
    """
    medias_list = Media.objects.all().order_by('year').reverse()
    renderdict = {
        'menu': {
            'media': 'active'
        },
        'medias': medias_list,
    }

    return render(request, "web/media.html", renderdict)


def links(request):
    """
    Links to partners
    """
    links_list = Link.objects.all().reverse()

    renderdict = {
        'menu': {
            'links': 'active'
        },
        'links': links_list,
    }

    return render(request, "web/links.html", renderdict)


def downloads(request):
    """
    Downloads available
    """
    download_list = Download.objects.all().reverse()

    renderdict = {
        'menu': {
            'downloads': 'active'
        },
        'downloads': download_list,
    }

    return render(request, "web/downloads.html", renderdict)


def contact(request):
    """
    Contact page
    """

    class PolitolocoForm(ModelForm):
        class Meta:
            model = Politoloco
            fields = ['email']

    success = 0
    failure = 0
    message = ''

    f = PolitolocoForm()
    if request.method == 'POST':
        add_f = PolitolocoForm(request.POST)
        if add_f.is_valid():
            add_f.save()
            success = 1
            message = 'E-Mail Adresse beim Newsletter von Politoloco registriert.'
        else:
            failure = 1
            message = 'E-Mail Adresse ungueltig'

    renderdict = {
        'menu': {
            'contact': 'active',
        },
        'request': request,
        'success': success,
        'failure': failure,
        'message': message
    }
    print(renderdict['menu'])

    return render(request, "web/contact.html", renderdict)


def myortoloco_home(request):
    """
    Overview on myortoloco
    """

    next_jobs = Job.objects.all()[0:7]
    teams = Taetigkeitsbereich.objects.all()

    renderdict = {
        'jobs': next_jobs,
        'teams': teams
    }

    return render(request, "myortoloco/home.html", renderdict)


def myortoloco_job(request, job_id):
    """
    Details for a job
    """
    print "gags"

    renderdict = {
        'job': get_object_or_404(Job, id=int(job_id))
    }

    return render(request, "myortoloco/job.html", renderdict)


def myortoloco_team(request, bereich_id):
    """
    Details for a team
    """

    job_types = JobTyp.objects.all().filter(bereich=bereich_id)

    jobs = Job.objects.all().filter(typ=job_types)

    renderdict = {
        'team': get_object_or_404(Taetigkeitsbereich, id=int(bereich_id)),
        'jobs': jobs,
    }

    return render(request, "myortoloco/team.html", renderdict)


def login(request):
    # If we submitted the form...
    if request.method == 'POST':

        # Check that the test cookie worked (we set it below):
        if request.session.test_cookie_worked():

            # The test cookie worked, so delete it.
            request.session.delete_test_cookie()

            # In practice, we'd need some logic to check username/password
            # here, but since this is an example...
            return HttpResponse("You're logged in.")

        # The test cookie failed, so display an error message. If this
        # were a real site, we'd want to display a friendlier message.
        else:
            return HttpResponse("Please enable cookies and try again.")

    # If we didn't post, send the test cookie along with the login form.
    request.session.set_test_cookie()
    return render(request, 'foo/login_form.html')


@login_required
def myortoloco_personal_info(request):
    print "susle"
    UserFormSet = modelformset_factory(User, fields=('first_name', 'last_name'))
    if (request.method == 'POST'):
        print "post"
        formset = UserFormSet(request.POST, queryset=User.objects.filter(id=request.user.id))
        if formset.is_valid():
            formset.save()
    else:
        print "other" + request.method
        formset = UserFormSet(queryset=User.objects.all().filter(id=request.user.id))

    renderdict = {
        'formset': formset
    }
    return render(request, "myortoloco/personal_info.html", renderdict)


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
    
