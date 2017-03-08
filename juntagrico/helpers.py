import sys
import hashlib
import subprocess
import datetime

from django.http import HttpResponse, HttpResponseServerError

from django.template.loader import get_template
from django.template import Context
from django.template.defaultfilters import slugify

from django.utils import timezone

from ics import Calendar, Event

from xhtml2pdf import pisa

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

import xlsxwriter
from StringIO import StringIO

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from config import *



class AuthenticateWithEmail(object):
    def authenticate(self, username=None, password=None):
        from models import Member

        try:
            user = Member.objects.get(**{'email': username}).user
            if user.check_password(password):
                return user
        except Member.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def render_to_pdf_http(request, template_name, renderdict, filename):
    """
    Take a string of rendered html and pack it into a pdfand return it thtough http
    """
    rendered_html = get_template(template_name).render(renderdict)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    success = pisa.CreatePDF(rendered_html, dest=response)

    if not success:
        return HttpResponseServerError()
    return response

def render_to_pdf_storage(template_name, renderdict, filename):
    """
    Take a string of rendered html and pack it into a pdfand save it
    """
    if default_storage.exists(filename):
        default_storage.delete(filename)
    rendered_html = get_template(template_name).render(renderdict)
    pdf = StringIO()
    pisa.CreatePDF(rendered_html, dest=pdf)
    default_storage.save(filename, ContentFile(pdf.getvalue()))

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
    return Job.objects.filter(time__gte=timezone.now()).order_by("time")

def get_current_one_time_jobs():
    from models import OneTimeJob
    return OneTimeJob.objects.filter(time__gte=timezone.now()).order_by("time")

def get_current_recuring_jobs():
    from models import RecuringJob
    return RecuringJob.objects.filter(time__gte=timezone.now()).order_by("time")

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


"""
    Generates excell for a defined set of fields and a model
"""
def generate_excell(fields, model_instance):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet(Config.members_string())

    col = 0
    for field in fields:
	parts = field.split('.')
	count =1
        dbfield = model_instance._meta.get_field(parts[0])
        while(count<len(parts)):
            dbfield = dbfield.related_model._meta.get_field(parts[count])
            count = count + 1
        worksheet_s.write_string(0, col, unicode(str(dbfield.verbose_name),"utf-8"))
        col = col + 1
        
    instances = model_instance.objects.all()
    
    row = 1
    for instance in instances:
        col =0
        for field in fields:
            parts = field.split('.')
	    count =1
            fieldvalue = getattr(instance, parts[0])
            while(count<len(parts) and fieldvalue is not None):
                fieldvalue = getattr(fieldvalue, parts[count])
                count = count + 1
            if fieldvalue is not None:
                if isinstance(fieldvalue,unicode):
                    worksheet_s.write_string(row, col, fieldvalue)
                else:
                    worksheet_s.write_string(row, col, unicode(str(fieldvalue),"utf-8"))
            col = col + 1
        row = row + 1
    
    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response

"""
    Create a ical string from an job
"""
def genecrate_ical_for_job(job):
    c = Calendar()
    e = Event()
    e.name = Config.organisation_name()+' Einsatz:'+job.typename
    e.location = job.typelocation
    e.description = job.typedescription
    e.begin = job.time.strftime('%Y%m%d %H:%M:%S')
    e.end = job.time.strftime('%Y%m%d %H:%M:%S')
    c.events.append(e)
    return str(c).replace("\n","\r\n")+'\r\n'
    
def start_of_year():
    year = timezone.now().year
    return datetime.date(year, 1, 1)
    
def start_of_next_year():
    year = timezone.now().year+1
    return datetime.date(year, 1, 1)
