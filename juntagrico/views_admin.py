# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Template, Context

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.extrasubscriptiondao import ExtraSubscriptionDao
from juntagrico.dao.mailtemplatedao import MailTemplateDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.models import *
from juntagrico.views import get_menu_dict
from juntagrico.util.jobs import *
from juntagrico.util.pdf import *
from juntagrico.util.xls import *
from juntagrico.util.mailer import *
from juntagrico.util.views_admin import *


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
    sender = request.POST.get('sender')
    if request.POST.get('allsubscription') == 'on':
        for member in MemberDao.members_for_email_with_subscription():
            emails.add(member.email)
    if request.POST.get('allshares') == 'on':
        for member in MemberDao.members_for_email():
            if member.share_set.count() > 0:
                emails.add(member.email)
    if request.POST.get('all') == 'on':
        for member in MemberDao.members_for_email():
            emails.add(member.email)
    if request.POST.get('recipients'):
        recipients = re.split(r'\s*,?\s*', request.POST.get('recipients'))
        for recipient in recipients:
            emails.add(recipient)
    if request.POST.get('allsingleemail'):
        emails |= set(request.POST.get('singleemail').split(' '))

    
    attachements = []
    append_attachements(request, attachements)

    if len(emails) > 0:
        send_filtered_mail(request.POST.get('subject'), request.POST.get('message'), request.POST.get('textMessage'),
                           emails, attachements, sender=sender)
        sent = len(emails)
    return redirect('/my/mails/send/result/' + str(sent) + '/')


@permission_required('juntagrico.can_send_mails')
def send_email_result(request, numsent):
    renderdict = get_menu_dict(request)
    renderdict.update({
        'sent': numsent
    })
    return render(request, 'mail_sender_result.html', renderdict)


@permission_required('juntagrico.can_send_mails')
def mails(request, enhanced=None):
    return my_mails_intern(request, enhanced)


@permission_required('juntagrico.is_depot_admin')
def mails_depot(request):
    return my_mails_intern(request, 'depot')


@permission_required('juntagrico.is_area_admin')
def mails_area(request):
    return my_mails_intern(request, 'area')


def my_mails_intern(request, enhanced, error_message=None):
    renderdict = get_menu_dict(request)
    renderdict.update({
        'recipient_type': request.POST.get('recipient_type'),
        'recipient_type_detail': request.POST.get('recipient_type_detail'),
        'recipients': request.POST.get('recipients'),
        'recipients_count': int(request.POST.get('recipients_count') or 0),
        'filter_value': request.POST.get('filter_value'),
        'mail_subject': request.POST.get('subject'),
        'mail_message': request.POST.get('message'),
        'enhanced': enhanced,
        'email': request.user.member.email,
        'error_message': error_message,
        'templates': MailTemplateDao.all_templates(),
        'can_use_general_email': request.user.has_perm('juntagrico.can_use_general_email'),
        'can_load_templates': request.user.has_perm('juntagrico.can_load_templates')
    })
    return render(request, 'mail_sender.html', renderdict)


@permission_required('juntagrico.can_filter_members')
def filters(request):
    now = timezone.now()
    members = MemberDao.members_with_assignments_count()
    renderdict = get_menu_dict(request)
    renderdict.update({
        'members': members
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_depot_admin')
def filters_depot(request, depot_id):
    now = timezone.now()
    depot = get_object_or_404(Depot, id=int(depot_id))
    members = MemberDao.members_with_assignments_count_for_depot(depot)
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails'] = True
    renderdict.update({
        'members': members,
        'enhanced': 'depot'
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_area_admin')
def filters_area(request, area_id):
    now = timezone.now()
    area = get_object_or_404(ActivityArea, id=int(area_id))
    members = MemberDao.members_with_assignments_count_in_area(area)
    renderdict = get_menu_dict(request)
    renderdict['can_send_mails'] = True
    renderdict.update({
        'members': members,
        'enhanced': 'area'
    })
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.can_filter_subscriptions')
def subscriptions(request):
    now = timezone.now()
    subscriptions = []
    for subscription in SubscriptionDao.all_subscritions():
        assignments = 0
        core_assignments = 0
        for member in MemberDao.members_with_assignments_count_in_subscription(subscription):
            assignments += member.assignment_count if member.assignment_count is not None else 0
            core_assignments += member.core_assignment_count if member.core_assignment_count is not None else 0

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
def filter_subscriptions_depot(request, depot_id):
    now = timezone.now()
    subscriptions = []
    depot = get_object_or_404(Depot, id=int(depot_id))
    for subscription in SubscriptionDao.subscritions_by_depot(depot):
        assignments = 0
        core_assignments = 0
        for member in  MemberDao.members_with_assignments_count_in_subscription(subscription):
            assignments += member.assignment_count if member.assignment_count is not None else 0
            core_assignments += member.core_assignment_count if member.core_assignment_count is not None else 0

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
    return alldepots_list('')


@permission_required('juntagrico.is_operations_group')
def future(request):
    renderdict = get_menu_dict(request)

    subscriptionsizes = []
    subscription_lines = dict({})
    extra_lines = dict({})
    for subscription_size in SubscriptionSizeDao.all_sizes_ordered():
        subscriptionsizes.append(subscription_size.name)
        subscription_lines[subscription_size.name] = {
            'name': subscription_size.name,
            'future': 0,
            'now': 0
        }
    for extra_subscription in ExtraSubscriptionTypeDao.all_extra_types():
        extra_lines[extra_subscription.name] = {
            'name': extra_subscription.name,
            'future': 0,
            'now': 0
        }
    for subscription in SubscriptionDao.all_active_subscritions():
        for subscription_size in subscriptionsizes:
            subscription_lines[subscription_size]['now'] += subscription.subscription_amount(subscription_size)
        for users_subscription in subscription.extra_subscriptions.all():
            extra_lines[users_subscription.type.name]['now'] += 1
            
    for subscription in SubscriptionDao.future_subscriptions():
        for subscription_size in subscriptionsizes:
            subscription_lines[subscription_size]['future'] += subscription.subscription_amount_future(
                subscription_size)
        for users_subscription in subscription.future_extra_subscriptions.all():
            extra_lines[users_subscription.type.name]['future'] += 1

    renderdict.update({
        'changed': request.GET.get('changed'),
        'subscription_lines': iter(subscription_lines.values()),
        'extra_lines': iter(extra_lines.values()),
    })
    return render(request, 'future.html', renderdict)



@permission_required('juntagrico.can_load_templates')
def get_mail_template(request, template_id):
    renderdict = {}

    template = MailTemplateDao.template_by_id(template_id)
    exec(template.code)
    t = Template(template.template)
    c = Context(renderdict)
    result = t.render(c)
    return HttpResponse(result)


@permission_required('juntagrico.is_operations_group')
def maps(request):
    renderdict = {
        'depots': DepotDao.all_depots(),
        'subscriptions': SubscriptionDao.all_active_subscritions(),
    }

    return render(request, 'maps.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def excel_export_members_filter(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = StringIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet_s = workbook.add_worksheet(Config.members_string())

    worksheet_s.write_string(0, 0, str('Name', 'utf-8'))
    worksheet_s.write_string(0, 1, str(Config.assignments_string(), 'utf-8'))
    worksheet_s.write_string(0, 2, str(Config.assignments_string() + ' Kernbereich', 'utf-8'))
    worksheet_s.write_string(0, 3, str('Taetigkeitsbereiche', 'utf-8'))
    worksheet_s.write_string(0, 4, str('Depot', 'utf-8'))
    worksheet_s.write_string(0, 5, str('Email', 'utf-8'))
    worksheet_s.write_string(0, 6, str('Telefon', 'utf-8'))
    worksheet_s.write_string(0, 7, str('Mobile', 'utf-8'))

    now = timezone.now()
    members = MemberDao.members_with_assignments_count()

    row = 1
    for member in members:
        member.all_areas = ''
        for area in member.areas.all():
            member.all_areas = member.all_areas + area.name + ' '
        if member.all_areas == '':
            member.all_areas = str('-Kein Tätigkeitsbereich-', 'utf-8')

        member.depot_name = str('Kein Depot definiert', 'utf-8')
        if member.subscription is not None:
            member.depot_name = member.subscription.depot.name
        looco_full_name = member.first_name + ' ' + member.last_name
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
def excel_export_members(request):
    fields = [
        'first_name',
        'last_name',
        'email',
        'addr_street',
        'addr_zipcode',
        'addr_location',
        'birthday',
        'phone',
        'mobile_phone',
        'confirmed',
        'reachable_by_email',
        'block_emails',
    ]
    return generate_excell(fields, Member)


@permission_required('juntagrico.is_operations_group')
def excel_export_shares(request):
    fields = [
        'number',
        'paid_date',
        'issue_date',
        'booking_date',
        'cancelled_date',
        'termination_date',
        'payback_date',
        'notes',
        'member.first_name',
        'member.last_name',
        'member.email',
    ]
    return generate_excell(fields, Share)


@permission_required('juntagrico.is_operations_group')
def export(request):
    renderdict = get_menu_dict(request)
    return render(request, 'export.html', renderdict)


@permission_required('juntagrico.is_operations_group')
def waitinglist(request):
    return subscription_management_list(SubscriptionDao.not_started_subscriptions(), get_menu_dict(request), 'waitinglist.html', request)
    
@permission_required('juntagrico.is_operations_group')
def canceledlist(request):
    return subscription_management_list(SubscriptionDao.canceled_subscriptions(), get_menu_dict(request), 'canceledlist.html', request)

    
@permission_required('juntagrico.is_operations_group')
def typechangelist(request):
    changedlist = []
    subscriptions = SubscriptionDao.all_active_subscritions()
    for subscription in subscriptions:
        if subscription.types_changed:
            changedlist.append(subscription)    
    return subscription_management_list(changedlist, get_menu_dict(request), 'typechangelist.html', request)
    
@permission_required('juntagrico.is_operations_group')
def extra_waitinglist(request):
    return subscription_management_list(ExtraSubscriptionDao.waiting_extra_subs(), get_menu_dict(request), 'extra_waitinglist.html', request)
    
@permission_required('juntagrico.is_operations_group')
def extra_canceledlist(request):
    return subscription_management_list(ExtraSubscriptionDao.canceled_extra_subs(), get_menu_dict(request), 'extra_canceledlist.html', request)
