import sys
import hashlib
import subprocess
import datetime

from django.http import HttpResponse, HttpResponseServerError

from django.template.loader import get_template
from django.template import Context
from django.template.defaultfilters import slugify

from xhtml2pdf import pisa

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required


class AuthenticateWithEmail(object):
    def authenticate(self, username=None, password=None):
        from models import Loco

        try:
            user = Loco.objects.get(**{'email': username}).user
            if user.check_password(password):
                return user
        except Loco.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def render_to_pdf(request, template_name, renderdict, filename):
    """
    Take a string of rendered html and pack it into a pdf.
    """
    rendered_html = get_template(template_name).render(Context(renderdict))

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response


weekday_choices = ((1, "Montag"),
                   (2, "Dienstag"),
                   (3, "Mittwoch"),
                   (4, "Donnerstag"),
                   (5, "Freitag"),
                   (6, "Samstag"),
                   (7, "Sonntag"))

weekdays = dict(weekday_choices)


def get_current_jobs():
    from models import Job

    return Job.objects.filter(time__gte=datetime.datetime.now()).order_by("time")

def get_current_one_time_jobs():
    from models import OneTimeJob

    return OneTimeJob.objects.filter(time__gte=datetime.datetime.now()).order_by("time")

def get_current_recuring_jobs():
    from models import RecuringJob

    return RecuringJob.objects.filter(time__gte=datetime.datetime.now()).order_by("time")

class Swapstd(object):
    def __init__(self, f=None, g=None):
        if g is None:
            g = f
        self.new = (f, g)
        self.old = (sys.stdout, sys.stderr)


    def __enter__(self):
        sys.stdout, sys.stderr = self.new


    def __exit__(self, *a):
        sys.stdout, sys.stderr = self.old


def make_username(firstname, lastname, email):
    firstname = slugify(firstname)[:10]
    lastname = slugify(lastname)[:10]
    email = hashlib.sha1(email).hexdigest()
    return ("%s_%s_%s" % (firstname, lastname, email))[:30]


@staff_member_required
def run_in_shell(request, command_string, input=None):
    p = subprocess.Popen(command_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(input)

    res = ("Finished running command:\n"
           "%s\n"
           "\n"
           "stdout:\n"
           "%s\n"
           "\n"
           "stderr:\n"
           "%s\n") % (command_string, out, err)
    return HttpResponse(res, content_type="text/plain")

def get_status_bean(percent=0):
        if percent >= 100:
            return "erbse_voll.png"
        elif percent >= 75:
            return "erbse_fast_voll.png"
        elif percent >= 50:
            return "erbse_halb.png"
        elif percent > 0:
            return "erbse_fast_leer.png"
        else:
            return "erbse_leer.png"

def get_status_bean_text(percent=0):
        if percent >= 100:
            return "Fertig"
        elif percent >= 75:
            return "Dreiviertel"
        elif percent >= 50:
            return "Halb"
        elif percent > 0:
            return "Angefangen"
        else:
            return "Nix"
          
"""
    Copys the user defined attributes of a model into another model. It will only copy the fields with are present in both
"""
def attribute_copy(source, target):
    for field in target._meta.fields:
                if(field.auto_created==False and field.editable==True and field.attname in source.__dict__ and field.attname in target.__dict__):
                    target.__dict__[field.attname] = source.__dict__[field.attname]
                    
            
