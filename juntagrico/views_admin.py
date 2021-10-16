import re
from io import BytesIO

from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Template, Context
from django.utils import timezone
from django.utils.translation import gettext as _
from xlsxwriter import Workbook

from juntagrico import version
from juntagrico.config import Config
from juntagrico.dao.mailtemplatedao import MailTemplateDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.sharedao import ShareDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionpartdao import SubscriptionPartDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.mailer import append_attachements
from juntagrico.mailer import formemails
from juntagrico.util import return_to_previous_location, addons
from juntagrico.util.management_list import get_changedate
from juntagrico.util.pdf import return_pdf_http
from juntagrico.util.subs import subscriptions_with_assignments
from juntagrico.util.views_admin import subscription_management_list
from juntagrico.util.xls import generate_excel
from juntagrico.view_decorators import any_permission_required
from juntagrico.views_subscription import error_page


@permission_required('juntagrico.can_send_mails')
def send_email(request):
    return send_email_intern(request)


@permission_required('juntagrico.is_depot_admin')
def send_email_depot(request):
    return send_email_intern(request)


@permission_required('juntagrico.is_area_admin')
def send_email_area(request):
    return send_email_intern(request)


@any_permission_required('juntagrico.is_area_admin', 'juntagrico.can_send_mails')
def send_email_job(request):
    return send_email_intern(request)


def send_email_intern(request):
    sent = 0
    if request.method != 'POST':
        raise Http404
    emails = set()
    sender = request.POST.get('sender')
    if request.POST.get('allsubscription') == 'on':
        m_emails = MemberDao.members_for_email_with_subscription().values_list('email',
                                                                               flat=True)
        emails.update(m_emails)
    if request.POST.get('allshares') == 'on':
        emails.update(MemberDao.members_for_email_with_shares(
        ).values_list('email', flat=True))
    if request.POST.get('all') == 'on':
        emails.update(MemberDao.members_for_email(
        ).values_list('email', flat=True))
    if request.POST.get('recipients'):
        emails.update(re.split(r'[\s,;]+', request.POST.get('recipients')))
    if request.POST.get('allsingleemail'):
        emails.update(re.split(r'[\s,;]+', request.POST.get('singleemail')))

    files = []
    append_attachements(request, files)

    if len(emails) > 0:
        formemails.internal(
            request.POST.get('subject'),
            request.POST.get('message'),
            request.POST.get('textMessage'),
            emails, files, sender=sender
        )
        sent = len(emails)
    return redirect('mail-result', numsent=sent)


@any_permission_required('juntagrico.can_send_mails',
                         'juntagrico.is_depot_admin',
                         'juntagrico.is_area_admin')
def send_email_result(request, numsent):
    renderdict = {
        'sent': numsent
    }
    return render(request, 'mail_sender_result.html', renderdict)


@permission_required('juntagrico.can_send_mails')
def mails(request, mail_url='mail-send'):
    return my_mails_intern(request, mail_url)


@permission_required('juntagrico.is_depot_admin')
def mails_depot(request):
    return my_mails_intern(request, 'mail-depot-send')


@permission_required('juntagrico.is_area_admin')
def mails_area(request):
    return my_mails_intern(request, 'mail-area-send')


@any_permission_required('juntagrico.is_area_admin', 'juntagrico.can_send_mails')
def mails_job(request):
    return my_mails_intern(request, 'mail-job-send')


def my_mails_intern(request, mail_url, error_message=None):
    renderdict = {
        'recipient_type': request.POST.get('recipient_type'),
        'recipient_type_detail': request.POST.get('recipient_type_detail'),
        'recipients': request.POST.get('recipients'),
        'recipients_count': int(request.POST.get('recipients_count') or 0),
        'filter_value': request.POST.get('filter_value'),
        'mail_subject': request.POST.get('subject'),
        'mail_message': request.POST.get('message'),
        'mail_url': mail_url,
        'email': request.user.member.email,
        'error_message': error_message,
        'templates': MailTemplateDao.all_templates(),
        'can_use_general_email': request.user.has_perm('juntagrico.can_use_general_email'),
        'can_load_templates': request.user.has_perm('juntagrico.can_load_templates')
    }
    return render(request, 'mail_sender.html', renderdict)


@any_permission_required('juntagrico.can_filter_members', 'juntagrico.change_member')
def filters_active(request):
    members = MemberDao.active_members()
    renderdict = {
        'members': members,
        'title': _('Alle aktiven {}').format(Config.vocabulary('member_pl'))
    }
    return render(request, 'members.html', renderdict)


@any_permission_required('juntagrico.can_filter_members', 'juntagrico.change_member')
def filters(request):
    members = MemberDao.all_members()
    renderdict = {
        'members': members,
        'title': _('Alle {}').format(Config.vocabulary('member_pl'))
    }
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_depot_admin')
def filters_depot(request, depot_id):
    depot = get_object_or_404(Depot, id=int(depot_id), contact=request.user.member)
    members = MemberDao.member_with_active_subscription_for_depot(depot)
    renderdict = {
        'can_send_mails': True,
        'members': members,
        'mail_url': 'mail-depot',
        'title': _('Alle aktiven {} im {} {}').format(Config.vocabulary('member_pl'), Config.vocabulary('depot'), depot.name)
    }
    return render(request, 'members.html', renderdict)


@permission_required('juntagrico.is_area_admin')
def filters_area(request, area_id):
    area = get_object_or_404(ActivityArea, id=int(area_id), coordinator=request.user.member)
    members = MemberDao.members_in_area(area)
    renderdict = {
        'can_send_mails': True,
        'members': members,
        'mail_url': 'mail-area',
        'title': _('Alle aktiven {} im Tätigkeitsbereich {}').format(Config.vocabulary('member_pl'), area.name)
    }
    return render(request, 'members.html', renderdict)


@any_permission_required('juntagrico.can_filter_subscriptions', 'juntagrico.change_subscription')
def subscriptions(request):
    renderdict = {
        'subscriptions': SubscriptionDao.all_active_subscritions(),
        'title': _('Alle aktiven {} im Überblick').format(Config.vocabulary('subscription_pl'))
    }

    return render(request, 'subscriptions.html', renderdict)


@permission_required('juntagrico.is_depot_admin')
def filter_subscriptions_depot(request, depot_id):
    depot = get_object_or_404(Depot, id=int(depot_id))
    renderdict = {
        'can_send_mails': True,
        'subscriptions': SubscriptionDao.active_subscritions_by_depot(depot),
        'mail_url': 'mail-depot',
        'title': _('Alle aktiven {} im {} {}').format(Config.vocabulary('subscription_pl'), Config.vocabulary('depot'), depot.name)
    }

    return render(request, 'subscriptions.html', renderdict)


@permission_required('juntagrico.can_view_lists')
def depotlist(request):
    return return_pdf_http('depotlist.pdf')


@permission_required('juntagrico.can_view_lists')
def depot_overview(request):
    return return_pdf_http('depot_overview.pdf')


@permission_required('juntagrico.can_view_lists')
def amount_overview(request):
    return return_pdf_http('amount_overview.pdf')


@permission_required('juntagrico.change_subscription')
def future(request):
    subscriptionsizes = []
    subscription_lines = dict({})
    for subscription_size in SubscriptionSizeDao.all_sizes_ordered():
        subscriptionsizes.append(subscription_size.id)
        subscription_lines[subscription_size.id] = {
            'name': subscription_size.product.name + '-' + subscription_size.name,
            'future': 0,
            'now': 0
        }
    for subscription in SubscriptionDao.all_active_subscritions():
        for subscription_size in subscriptionsizes:
            subscription_lines[subscription_size]['now'] += subscription.subscription_amount(
                subscription_size)

    for subscription in SubscriptionDao.future_subscriptions():
        for subscription_size in subscriptionsizes:
            subscription_lines[subscription_size]['future'] += subscription.subscription_amount_future(
                subscription_size)

    renderdict = {
        'changed': request.GET.get('changed'),
        'subscription_lines': iter(subscription_lines.values()),
    }
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


@permission_required('juntagrico.can_view_exports')
def excel_export_members_filter(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = Workbook(output)
    worksheet_s = workbook.add_worksheet(Config.vocabulary('member_pl'))

    worksheet_s.write_string(0, 0, str(_('Name')))
    worksheet_s.write_string(0, 1, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(
        0, 2, str(Config.vocabulary('assignment') + ' ' + _('Kernbereich')))
    worksheet_s.write_string(0, 3, str(_('Taetigkeitsbereiche')))
    worksheet_s.write_string(0, 4, str(_('Depot')))
    worksheet_s.write_string(0, 5, str(_('Email')))
    worksheet_s.write_string(0, 6, str(_('Telefon')))
    worksheet_s.write_string(0, 7, str(_('Mobile')))
    members = MemberDao.members_with_assignments_count()

    row = 1
    for member in members:
        member.all_areas = ''
        for area in member.areas.all():
            member.all_areas = member.all_areas + area.name + ' '
        if member.all_areas == '':
            member.all_areas = str(_('-Kein Tätigkeitsbereich-'))

        member.depot_name = str(_('Kein Depot definiert'))
        if member.subscription_current is not None:
            member.depot_name = member.subscription_current.depot.name
        full_name = member.first_name + ' ' + member.last_name
        worksheet_s.write_string(row, 0, full_name)
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


@permission_required('juntagrico.can_view_exports')
def excel_export_subscriptions(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = Workbook(output)
    worksheet_s = workbook.add_worksheet(Config.vocabulary('subscription_pl'))

    worksheet_s.write_string(0, 0, str(_('Übersicht')))
    worksheet_s.write_string(0, 1, str(_('HauptbezieherIn')))
    worksheet_s.write_string(0, 2, str(_('HauptbezieherInEmail')))
    worksheet_s.write_string(0, 3, str(_('HauptbezieherInTelefon')))
    worksheet_s.write_string(0, 4, str(_('HauptbezieherInMobile')))
    worksheet_s.write_string(0, 5, str(_('Weitere BezieherInnen')))
    worksheet_s.write_string(0, 6, str(_('Status')))
    worksheet_s.write_string(0, 7, str(_('Depot')))
    worksheet_s.write_string(0, 8, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(0, 9, str(_('{} soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 10, str(_('{} status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 11, str(_('{} Kernbereich'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 12, str(_('{} Kernbereich soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 13, str(_('{} Kernbereich status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 14, str(_('Preis')))

    subs = subscriptions_with_assignments(SubscriptionDao.all_subscritions())

    row = 1
    for sub in subs:
        primary_member = sub['subscription'].primary_member
        if primary_member is not None:
            name = primary_member.get_name()
            email = primary_member.email
            phone = primary_member.phone or ''
            mobile = primary_member.mobile_phone or ''
        else:
            name = ''
            email = ''
            phone = ''
            mobile = ''

        worksheet_s.write_string(row, 0, sub['subscription'].size)
        worksheet_s.write_string(row, 1, name)
        worksheet_s.write_string(row, 2, email)
        worksheet_s.write_string(row, 3, phone)
        worksheet_s.write_string(row, 4, mobile)
        worksheet_s.write_string(row, 5, sub['subscription'].other_recipients_names)
        worksheet_s.write_string(row, 6, sub['subscription'].state_text)
        worksheet_s.write_string(row, 7, sub['subscription'].depot.name)
        worksheet_s.write(row, 8, sub.get('assignments'))
        worksheet_s.write(row, 9, sub['subscription'].required_assignments)
        worksheet_s.write(row, 10, sub.get('assignments_progress'))
        worksheet_s.write(row, 11, sub.get('core_assignments'))
        worksheet_s.write(row, 12, sub['subscription'].required_core_assignments)
        worksheet_s.write(row, 13, sub.get('core_assignments_progress'))
        worksheet_s.write(row, 14, sub['subscription'].price)
        row += 1

    workbook.close()
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response


@permission_required('juntagrico.can_view_exports')
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
        'deactivation_date',
    ]
    return generate_excel(fields, Member)


@permission_required('juntagrico.can_view_exports')
def excel_export_shares(request):
    fields = [
        'id',
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
    return generate_excel(fields, Share)


@permission_required('juntagrico.can_view_exports')
def export(request):
    return render(request, 'export.html', {})


@permission_required('juntagrico.change_subscription')
def waitinglist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionDao.not_started_subscriptions(), render_dict,
                                        'management_lists/waitinglist.html', request)


@permission_required('juntagrico.change_subscription')
def canceledlist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionDao.canceled_subscriptions(), render_dict,
                                        'management_lists/canceledlist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def part_waitinglist(request):
    render_dict = get_changedate(request)
    changedlist = SubscriptionPartDao.waiting_parts_for_active_subscriptions()
    return subscription_management_list(changedlist, render_dict, 'management_lists/part_waitinglist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def part_canceledlist(request):
    render_dict = get_changedate(request)
    changedlist = SubscriptionPartDao.canceled_parts_for_active_subscriptions()
    return subscription_management_list(changedlist, render_dict, 'management_lists/part_canceledlist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def extra_waitinglist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionPartDao.waiting_extra_subs(), render_dict,
                                        'management_lists/extra_waitinglist.html', request)


@permission_required('juntagrico.change_subscriptionpart')
def extra_canceledlist(request):
    render_dict = get_changedate(request)
    return subscription_management_list(SubscriptionPartDao.canceled_extra_subs(), render_dict,
                                        'management_lists/extra_canceledlist.html', request)


@permission_required('juntagrico.change_share')
def share_canceledlist(request):
    render_dict = {'change_date_disabled': True}
    return subscription_management_list(ShareDao.canceled_shares(), render_dict,
                                        'management_lists/share_canceledlist.html', request)


@permission_required('juntagrico.change_member')
def member_canceledlist(request):
    render_dict = {'change_date_disabled': True}
    return subscription_management_list(MemberDao.canceled_members(), render_dict,
                                        'management_lists/member_canceledlist.html', request)


@permission_required('juntagrico.change_member')
def deactivate_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.deactivation_date = timezone.now().date()
    member.save()
    return return_to_previous_location(request)


def set_change_date(request):
    if request.method != 'POST':
        raise Http404
    raw_date = request.POST.get('date')
    try:
        date = timezone.datetime.strptime(raw_date, '%m/%d/%Y').date()
        request.session['changedate'] = date
    except ValueError:
        return error_page(request, _('Bitte gib ein Datum im Format MM/TT/JJJJ ein.'))
    return return_to_previous_location(request)


def unset_change_date(request):
    request.session['changedate'] = None
    return return_to_previous_location(request)


@permission_required('juntagrico.change_subscription')
def sub_inconsistencies(request):
    management_list = []
    for sub in SubscriptionDao.all_subscritions():
        try:
            sub.clean()
            for part in sub.parts.all():
                part.clean()
            for member in sub.subscriptionmembership_set.all():
                member.clean()
        except Exception as e:
            management_list.append({'subscription': sub, 'error': e})
        if sub.primary_member is None:
            management_list.append({'subscription': sub, 'error': _('Haubtbezieher ist nicht gesetzt')})
    render_dict = {'change_date_disabled': True,
                   'email_form_disabled': True}
    return subscription_management_list(management_list, render_dict,
                                        'management_lists/inconsistent.html', request)


@permission_required('juntagrico.change_assignment')
def assignments(request):
    management_list = subscriptions_with_assignments(SubscriptionDao.all_active_subscritions())
    render_dict = {'change_date_disabled': True}
    return subscription_management_list(management_list, render_dict,
                                        'management_lists/assignments.html', request)


def versions(request):
    versions = {'juntagrico': version}
    versions.update(addons.config.get_versions())
    render_dict = {'versions': versions}
    return render(request, 'versions.html', render_dict)
