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
from django.db.models import Count, Case, When
from django.db import models
from django.utils import timezone
from django.template import Template, Context

import xlsxwriter

from my_ortoloco.models import *
from my_ortoloco.forms import *
from my_ortoloco.helpers import *
from my_ortoloco.filters import Filter
from my_ortoloco.mailer import *
from my_ortoloco.views import get_menu_dict

from static_ortoloco.models import StaticContent

import hashlib
from static_ortoloco.models import Politoloco

from decorators import primary_loco_of_abo


@permission_required('my_ortoloco.can_send_mails')
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
        for loco in Loco.objects.exclude(abo=None).filter(abo__active=True).exclude(block_emails=True):
            emails.add(loco.email)
    if request.POST.get("allanteilsschein") == "on":
        for loco in Loco.objects.exclude(block_emails=True):
            if loco.anteilschein_set.count() > 0:
                emails.add(loco.email)
    if request.POST.get("all") == "on":
        for loco in Loco.objects.exclude(block_emails=True):
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
    return redirect("/my/mails/send/result/"+str(sent)+"/") 


def send_email_result(request, numsent):
    renderdict = get_menu_dict(request)
    renderdict.update({
        'sent': numsent
    })
    return render(request, 'mail_sender_result.html', renderdict)

@permission_required('my_ortoloco.can_send_mails')
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
        'error_message': error_message,
        'templates': MailTemplate.objects.all(),
        'can_use_general_email': request.user.has_perm('my_ortoloco.can_use_general_email')
    })
    return render(request, 'mail_sender.html', renderdict)

@permission_required('my_ortoloco.can_filter_locos')
def my_filters(request):
    now = timezone.now()
    locos = Loco.objects.annotate(boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, then=1)))).annotate(core_boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, boehnli__core_cache=True, then=1))))
    renderdict = get_menu_dict(request)
    renderdict.update({
        'locos': locos
    })
    return render(request, 'filters.html', renderdict)



@permission_required('my_ortoloco.is_depot_admin')
def my_filters_depot(request, depot_id):
    now = timezone.now()
    depot = get_object_or_404(Depot, id=int(depot_id))
    locos = Loco.objects.filter(abo__depot = depot).annotate(boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, then=1)))).annotate(core_boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, boehnli__core_cache=True, then=1))))
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails']=True
    renderdict.update({
        'locos': locos,
        'enhanced': "depot"
    })
    return render(request, 'filters.html', renderdict)

@permission_required('my_ortoloco.is_area_admin')
def my_filters_area(request, area_id):
    now = timezone.now()
    area = get_object_or_404(Taetigkeitsbereich, id=int(area_id))
    locos = area.locos.all().annotate(boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, then=1)))).annotate(core_boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, boehnli__core_cache=True, then=1))))
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails']=True
    renderdict.update({
        'locos': locos,
        'enhanced': "area"
    })
    return render(request, 'filters.html', renderdict)


@permission_required('my_ortoloco.can_filter_abos')
def my_abos(request):
    now = timezone.now()
    abos = []
    for abo in Abo.objects.filter():
        boehnlis = 0
        boehnlis_kernbereich = 0
        for loco in abo.locos.annotate(boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, then=1)))).annotate(core_boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, boehnli__core_cache=True, then=1)))):
            boehnlis += loco.boehnli_count
            boehnlis_kernbereich += loco.core_boehnli_count

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
    now = timezone.now()
    abos = []
    depot = get_object_or_404(Depot, id=int(depot_id))
    for abo in Abo.objects.filter(depot = depot):
        boehnlis = 0
        boehnlis_kernbereich = 0
        for loco in abo.locos.annotate(boehnli_count=Count(Case(When(boehnli__job__time__year=now.year, boehnli__job__time__lt=now, then=1)))).annotate(core_boehnli_count=Count(Case(When(boehnli__job__time__year=d.year, boehnli__job__time__lt=d, boehnli__core_cache=True, then=1)))):
            boehnlis += loco.boehnli_count
            boehnlis_kernbereich += loco.core_boehnli_count

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

@permission_required('my_ortoloco.is_operations_group')
def my_depotlisten(request):
    return alldepots_list(request, "")
    
@permission_required('my_ortoloco.is_operations_group')
def alldepots_list(request, name):
    """
    Printable list of all depots to check on get gemüse
    """
    if name == "":
        depots = Depot.objects.all().order_by("code")
    else:
        depots = [get_object_or_404(Depot, code__iexact=name)]

    categories = []
    types =[]
    for category in ExtraAboCategory.objects.all().order_by("sort_order"):
            cat={}
            cat["name"]= category.name
            cat["description"] = category.description
            count = 0
            for extra_abo in ExtraAboType.objects.all().filter(category = category).order_by("sort_order"):
                count+=1
                type={}
                type["name"] = extra_abo.name
                type["size"] = extra_abo.size
                type["last"]=False
                types.append(type)
            type["last"]=True
            cat["count"] = count
            categories.append(cat)    
    
    overview = {
        'Dienstag': None,
        'Donnerstag': None,
        'all': None
    }
    
    count = len(types)+2
    overview["Dienstag"] = [0]*count
    overview["Donnerstag"] = [0]*count
    overview["all"] = [0]*count
        
    all = overview.get('all')
    
    for depot in depots:
        depot.fill_overview_cache()
        depot.fill_active_abo_cache()
        row = overview.get(depot.get_weekday_display())
        count=0
        while count < len(row):
            row[count] += depot.overview_cache[count]
            all[count] += depot.overview_cache[count]
            count+=1; 
        
    overview["Dienstag"].insert(2, overview["Dienstag"][0]+2*overview["Dienstag"][1])
    overview["Donnerstag"].insert(2, overview["Donnerstag"][0]+2*overview["Donnerstag"][1])
    overview["all"].insert(2, overview["all"][0]+2*overview["all"][1])
        
    renderdict = {
        "overview": overview,
        "depots": depots,
        "categories" : categories,
        "types" : types,
        "datum": timezone.now()
    }

    return render_to_pdf_http(request, "exports/all_depots.html", renderdict, 'Depotlisten')


@permission_required('my_ortoloco.is_operations_group')
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


@permission_required('my_ortoloco.is_operations_group')
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

@permission_required('my_ortoloco.is_operations_group')
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

@permission_required('my_ortoloco.is_operations_group')
def my_get_mail_template(request, template_id):
    renderdict = {}

    template = MailTemplate.objects.filter(id = template_id)[0]
    exec(template.code)
    t = Template(template.template)
    c = Context(renderdict)
    result = t.render(c)
    return HttpResponse(result)


@permission_required('my_ortoloco.is_operations_group')
def my_maps(request):

    renderdict = {
        "depots": Depot.objects.all(),
        "locos" : Loco.objects.all(),
    }

    return render(request, "maps.html", renderdict)


@permission_required('my_ortoloco.is_operations_group')
def my_excel_export_locos_filter(request):
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

@permission_required('my_ortoloco.is_operations_group')
def my_excel_export_locos(request):
    fields = [
    u'first_name',
    u'last_name',
    u'email',
    u'addr_street',
    u'addr_zipcode',
    u'addr_location',
    u'birthday',
    u'phone',
    u'mobile_phone',
    u'confirmed',
    u'reachable_by_email',
    u'block_emails',
    ]
    return generate_excell(fields, Loco)
    
@permission_required('my_ortoloco.is_operations_group')
def my_excel_export_shares(request):
    fields = [
    u'number',
    u'paid_date',
    u'issue_date',
    u'booking_date',
    u'cancelled_date',
    u'termination_date',
    u'payback_date',
    u'notes',
    u'loco.first_name',
    u'loco.last_name',
    u'loco.email',
    ]
    return generate_excell(fields, Anteilschein)

@permission_required('my_ortoloco.is_operations_group')
def my_export(request):
    renderdict = get_menu_dict(request)
    return render(request, 'export.html', renderdict)
    



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








