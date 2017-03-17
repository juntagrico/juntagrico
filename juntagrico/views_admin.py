# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Case, When
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Template, Context

from juntagrico.models import *
from juntagrico.views import get_menu_dict
from juntagrico.util.jobs import *
from juntagrico.util.pdf import *
from juntagrico.util.xls import *


@permission_required('juntagrico.can_send_mails')
def send_email(request):
    return send_email_intern(request)


@permission_required('juntagrico.is_depot_admin')
def send_email_depot(request):
    return send_email_intern(request)


@permission_required('juntagrico.is_area_admin')
def send_email_area(request):
    return send_email_intern(request)


def send_email_intern(request):
    sent = 0
    if request.method != 'POST':
        raise Http404
    emails = set()
    sender = request.POST.get("sender")
    if request.POST.get("allsubscription") == "on":
        for member in Member.objects.exclude(subscription=None).filter(subscription__active=True).exclude(
                block_emails=True):
            emails.add(member.email)
    if request.POST.get("share") == "on":
        for member in Member.objects.exclude(block_emails=True):
            if member.share_set.count() > 0:
                emails.add(member.email)
    if request.POST.get("all") == "on":
        for member in Member.objects.exclude(block_emails=True):
            emails.add(member.email)
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
        send_filtered_mail(request.POST.get("subject"), request.POST.get("message"), request.POST.get("textMessage"),
                           emails, request.META["HTTP_HOST"], attachements, sender=sender)
        sent = len(emails)
    return redirect("/my/mails/send/result/" + str(sent) + "/")


@permission_required('juntagrico.can_send_mails')
def send_email_result(request, numsent):
    renderdict = get_menu_dict(request)
    renderdict.update({
        'sent': numsent
    })
    return render(request, 'mail_sender_result.html', renderdict)


@permission_required('juntagrico.can_send_mails')
def my_mails(request, enhanced=None):
    return my_mails_intern(request, enhanced)


@permission_required('juntagrico.is_depot_admin')
def my_mails_depot(request):
    return my_mails_intern(request, "depot")


@permission_required('juntagrico.is_area_admin')
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
        'email': request.user.member.email,
        'error_message': error_message,
        'templates': MailTemplate.objects.all(),
        'can_use_general_email': request.user.has_perm('juntagrico.can_use_general_email')
    })
    return render(request, 'mail_sender.html', renderdict)


@permission_required('juntagrico.can_filter_members')
def my_filters(request):
    now = timezone.now()
    members = Member.objects.annotate(assignment_count=Count(
        Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
        core_assignment_count=Count(Case(
            When(assignment__job__time__year=now.year, assignment__job__time__lt=now, assignment__core_cache=True,
                 then=1))))
    renderdict = get_menu_dict(request)
    renderdict.update({
        'members': members
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_depot_admin')
def my_filters_depot(request, depot_id):
    now = timezone.now()
    depot = get_object_or_404(Depot, id=int(depot_id))
    members = Member.objects.filter(subscription__depot=depot).annotate(assignment_count=Count(
        Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
        core_assignment_count=Count(Case(
            When(assignment__job__time__year=now.year, assignment__job__time__lt=now, assignment__core_cache=True,
                 then=1))))
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails'] = True
    renderdict.update({
        'members': members,
        'enhanced': "depot"
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_area_admin')
def my_filters_area(request, area_id):
    now = timezone.now()
    area = get_object_or_404(ActivityArea, id=int(area_id))
    members = area.members.all().annotate(assignment_count=Count(
        Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
        core_assignment_count=Count(Case(
            When(assignment__job__time__year=now.year, assignment__job__time__lt=now, assignment__core_cache=True,
                 then=1))))
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails'] = True
    renderdict.update({
        'members': members,
        'enhanced': "area"
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.can_filter_subscriptions')
def my_subscriptions(request):
    now = timezone.now()
    subscriptions = []
    for subscription in Subscription.objects.filter():
        assignments = 0
        core_assignments = 0
        for member in subscription.members.annotate(assignment_count=Count(
                Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
            core_assignment_count=Count(Case(
                When(assignment__job__time__year=now.year, assignment__job__time__lt=now,
                     assignemnt__core_cache=True, then=1)))):
            assignments += member.assignment_count
            core_assignments += member.core_assignment_count

        subscriptions.append({
            'subscription': subscription,
            'text': get_status_image_text(100 / (subscription.size * 10) * assignments if subscription.size > 0 else 0),
            'assignments': assignments,
            'core_assignments': core_assignments,
            'icon': get_status_image(
                100 / (subscription.size * 10) * assignments if subscription.size > 0 else 0)
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'subscriptions': subscriptions
    })

    return render(request, 'subscriptions.html', renderdict)


@permission_required('juntagrico.is_depot_admin')
def my_subscriptions_depot(request, depot_id):
    now = timezone.now()
    subscriptions = []
    depot = get_object_or_404(Depot, id=int(depot_id))
    for subscription in Subscription.objects.filter(depot=depot):
        assignments = 0
        core_assignments = 0
        for member in subscription.members.annotate(assignment_count=Count(
                Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
            core_assignment_count=Count(Case(
                When(assignment__job__time__year=now.year, assignment__job__time__lt=now,
                     assignment__core_cache=True, then=1)))):
            assignments += member.assignment_count
            core_assignments += member.core_assignemtns_count

        subscriptions.append({
            'subscription': subscription,
            'text': get_status_image_text(100 / (subscription.size * 10) * assignments if subscription.size > 0 else 0),
            'assignments': assignments,
            'core_assignments': core_assignments,
            'icon': get_status_image(
                100 / (subscription.size * 10) * assignments if subscription.size > 0 else 0)
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'subscriptions': subscriptions
    })

    return render(request, 'subscriptions.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def my_depotlists():
    return alldepots_list("")


@permission_required('juntagrico.is_operations_group')
def alldepots_list(name):
    """
    Printable list of all depots to check on get gemüse
    """
    if name == "":
        depots = Depot.objects.all().order_by("code")
    else:
        depots = [get_object_or_404(Depot, code__iexact=name)]

    categories = []
    types = []
    for category in ExtraSubscriptionCategory.objects.all().order_by("sort_order"):
        cat = {"name": category.name, "description": category.description}
        count = 0
        for extra_subscription in ExtraSubscriptionType.objects.all().filter(category=category).order_by("sort_order"):
            count += 1
            type = {"name": extra_subscription.name, "size": extra_subscription.size, "last": False}
            types.append(type)
        type["last"] = True
        cat["count"] = count
        categories.append(cat)

    overview = {
        'Dienstag': None,
        'Donnerstag': None,
        'all': None
    }

    count = len(types) + 2
    overview["Dienstag"] = [0] * count
    overview["Donnerstag"] = [0] * count
    overview["all"] = [0] * count

    all = overview.get('all')

    for depot in depots:
        depot.fill_overview_cache()
        depot.fill_active_subscription_cache()
        row = overview.get(depot.get_weekday_display())
        count = 0
        while count < len(row):
            row[count] += depot.overview_cache[count]
            all[count] += depot.overview_cache[count]
            count += 1

    overview["Dienstag"].insert(2, overview["Dienstag"][0] + 2 * overview["Dienstag"][1])
    overview["Donnerstag"].insert(2, overview["Donnerstag"][0] + 2 * overview["Donnerstag"][1])
    overview["all"].insert(2, overview["all"][0] + 2 * overview["all"][1])

    renderdict = {
        "overview": overview,
        "depots": depots,
        "categories": categories,
        "types": types,
        "datum": timezone.now()
    }

    return render_to_pdf_http("exports/all_depots.html", renderdict, 'Depotlisten')


@permission_required('juntagrico.is_operations_group')
def my_future(request):
    renderdict = get_menu_dict(request)

    subscriptionsizes = []
    subscription_lines = dict({})
    extra_lines = dict({})
    for subscription_size in SubscriptionSize.objects.all():
        subscriptionsizes.append(subscription_size.name)
        subscription_lines[subscription_size.name] = {
            'name': subscription_size.name,
            'future': 0,
            'now': 0
        }
    for extra_subscription in ExtraSubscriptionType.objects.all():
        extra_lines[extra_subscription.name] = {
            'name': extra_subscription.name,
            'future': 0,
            'now': 0
        }
    for subscription in Subscription.objects.all():
        for subscription_size in subscriptionsizes:
            subscription_lines[subscription_size]['now'] += subscription.subscription_amount(subscription_size)
            subscription_lines[subscription_size]['future'] += subscription.subscription_amount_future(
                subscription_size)
        for users_subscription in subscription.future_extra_subscriptions.all():
            extra_lines[users_subscription.type.name]['future'] += 1
        for users_subscription in subscription.extra_subscriptions.all():
            extra_lines[users_subscription.type.name]['now'] += 1

    month = int(time.strftime("%m"))
    day = int(time.strftime("%d"))

    renderdict.update({
        'changed': request.GET.get("changed"),
        'subscription_lines': subscription_lines.itervalues(),
        'extra_lines': extra_lines.itervalues(),
        'subscription_change_enabled': month is 12 or (month is 1 and day <= 6)
    })
    return render(request, 'future.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def my_switch_extras():
    for subscription in Subscription.objects.all():
        for extra in subscription.extra_subscription_set:
            if extra.active is True and extra.canceled is True:
                extra.active = False
                extra.save()
            elif extra.active is False and extra.deactivation_date is None:
                extra.active = True
                extra.save()

    return redirect('/my/zukunft?changed=true')


@permission_required('juntagrico.is_operations_group')
def my_switch_subscriptions(request):
    renderdict = get_menu_dict(request)

    for subscription in Subscription.objects.all():
        if subscription.size is not subscription.future_size:
            if subscription.future_size is 0:
                subscription.active = False
            if subscription.size is 0:
                subscription.active = True
            subscription.size = subscription.future_size
            subscription.save()

    renderdict.update({
    })

    return redirect('/my/zukunft?changed=true')


@permission_required('juntagrico.is_operations_group')
def my_get_mail_template(template_id):
    renderdict = {}

    template = MailTemplate.objects.filter(id=template_id)[0]
    exec template.code
    t = Template(template.template)
    c = Context(renderdict)
    result = t.render(c)
    return HttpResponse(result)


@permission_required('juntagrico.is_operations_group')
def my_maps(request):
    renderdict = {
        "depots": Depot.objects.all(),
        "subscriptions": Subscription.objects.filter(active=True),
    }

    return render(request, "maps.html", renderdict)


@permission_required('juntagrico.is_operations_group')
def my_excel_export_members_filter():
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet(Config.members_string())

    worksheet_s.write_string(0, 0, unicode("Name", "utf-8"))
    worksheet_s.write_string(0, 1, unicode(Config.assignments_string(), "utf-8"))
    worksheet_s.write_string(0, 2, unicode(Config.assignments_string() + " Kernbereich", "utf-8"))
    worksheet_s.write_string(0, 3, unicode("Taetigkeitsbereiche", "utf-8"))
    worksheet_s.write_string(0, 4, unicode("Depot", "utf-8"))
    worksheet_s.write_string(0, 5, unicode("Email", "utf-8"))
    worksheet_s.write_string(0, 6, unicode("Telefon", "utf-8"))
    worksheet_s.write_string(0, 7, unicode("Mobile", "utf-8"))

    now = timezone.now()
    members = Member.objects.annotate(assignment_count=Count(
        Case(When(assignment__job__time__year=now.year, assignment__job__time__lt=now, then=1)))).annotate(
        core_assignment_count=Count(Case(
            When(assignment__job__time__year=now.year, assignment__job__time__lt=now, assignment__core_cache=True,
                 then=1))))

    row = 1
    for member in members:
        member.all_areas = ""
        for area in member.areas.all():
            member.all_areas = member.all_areas + area.name + " "
        if member.all_areas == "":
            member.all_areas = unicode("-Kein Tätigkeitsbereich-", "utf-8")

        member.depot_name = unicode("Kein Depot definiert", "utf-8")
        if member.subscription is not None:
            member.depot_name = member.subscription.depot.name
        looco_full_name = member.first_name + " " + member.last_name
        worksheet_s.write_string(row, 0, looco_full_name)
        worksheet_s.write(row, 1, member.assignment_count)
        worksheet_s.write(row, 2, member.core_assignment_count)
        worksheet_s.write_string(row, 3, member.all_areas)
        worksheet_s.write_string(row, 4, member.depot_name)
        worksheet_s.write_string(row, 5, member.email)
        worksheet_s.write_string(row, 6, member.phone)
        if member.mobile_phone is not None:
            worksheet_s.write_string(row, 7, member.mobile_phone)
        row += 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response


@permission_required('juntagrico.is_operations_group')
def my_excel_export_members():
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
    return generate_excell(fields, Member)


@permission_required('juntagrico.is_operations_group')
def my_excel_export_shares():
    fields = [
        u'number',
        u'paid_date',
        u'issue_date',
        u'booking_date',
        u'cancelled_date',
        u'termination_date',
        u'payback_date',
        u'notes',
        u'member.first_name',
        u'member.last_name',
        u'member.email',
    ]
    return generate_excell(fields, Share)


@permission_required('juntagrico.is_operations_group')
def my_export(request):
    renderdict = get_menu_dict(request)
    return render(request, 'export.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def waitinglist(request):
    renderdict = get_menu_dict(request)
    waitinglist = Subscription.objects.filter(active=False).filter(deactivation_date=None).order_by('start_date')
    renderdict.update({
        'waitinglist': waitinglist
    })
    return render(request, 'waitinglist.html', renderdict)
