from io import BytesIO

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from xlsxwriter import Workbook

from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription

from juntagrico.util.management_list import get_changedate
from juntagrico.util.xls import generate_excel

from juntagrico_legacy.dao.subscriptiondao import SubscriptionDao
from juntagrico_legacy.dao.subscriptionpartdao import SubscriptionPartDao


def subscription_management_list(management_list, renderdict, template, request):
    renderdict.update({
        'management_list': management_list,
    })
    return render(request, template, renderdict)


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


@permission_required('juntagrico.can_view_exports')
def excel_export_members_filter(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    output = BytesIO()
    workbook = Workbook(output)
    worksheet_s = workbook.add_worksheet(str(Config.vocabulary('member_pl')))

    worksheet_s.write_string(0, 0, str(_('Name')))
    worksheet_s.write_string(0, 1, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(
        0, 2, str(Config.vocabulary('assignment') + ' ' + str(_('Kernbereich'))))
    worksheet_s.write_string(0, 3, str(_('Taetigkeitsbereiche')))
    worksheet_s.write_string(0, 4, str(_('Depot')))
    worksheet_s.write_string(0, 5, str(_('Email')))
    worksheet_s.write_string(0, 6, str(_('Telefon')))
    worksheet_s.write_string(0, 7, str(_('Mobile')))

    row = 1
    for member in Member.objects.annotate_all_assignment_count():
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
    worksheet_s = workbook.add_worksheet(str(Config.vocabulary('subscription_pl')))

    worksheet_s.write_string(0, 0, str(_('Übersicht')))
    worksheet_s.write_string(0, 1, str(_('HauptbezieherIn')))
    worksheet_s.write_string(0, 2, str(_('HauptbezieherInEmail')))
    worksheet_s.write_string(0, 3, str(_('HauptbezieherInTelefon')))
    worksheet_s.write_string(0, 4, str(_('HauptbezieherInMobile')))
    worksheet_s.write_string(0, 5, str(_('Weitere BezieherInnen')))
    worksheet_s.write_string(0, 6, str(_('Status')))
    worksheet_s.write_string(0, 7, str(_('Kündigungsdatum')))
    worksheet_s.write_string(0, 8, str(_('Depot')))
    worksheet_s.write_string(0, 9, str(Config.vocabulary('assignment')))
    worksheet_s.write_string(0, 10, str(_('{} soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 11, str(_('{} status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 12, str(_('{} Kernbereich'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 13, str(_('{} Kernbereich soll'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 14, str(_('{} Kernbereich status(%)'.format(Config.vocabulary('assignment')))))
    worksheet_s.write_string(0, 15, str(_('Preis')))

    subs = Subscription.objects.all().annotate_assignments_progress().select_related('primary_member')

    row = 1
    for sub in subs:
        primary_member = sub.primary_member
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

        c_date = ''
        if sub.cancellation_date:
            c_date = sub.cancellation_date.strftime('%d/%m/%y')

        worksheet_s.write_string(row, 0, sub.size)
        worksheet_s.write_string(row, 1, name)
        worksheet_s.write_string(row, 2, email)
        worksheet_s.write_string(row, 3, phone)
        worksheet_s.write_string(row, 4, mobile)
        worksheet_s.write_string(row, 5, ', '.join(str(m) for m in sub.co_members()))
        worksheet_s.write_string(row, 6, sub.state_text)
        worksheet_s.write_string(row, 7, c_date)
        worksheet_s.write_string(row, 8, sub.depot.name)
        worksheet_s.write(row, 9, sub.assignment_count)
        worksheet_s.write(row, 10, sub.required_assignments)
        worksheet_s.write(row, 11, sub.assignments_progress)
        worksheet_s.write(row, 12, sub.core_assignment_count)
        worksheet_s.write(row, 13, sub.required_core_assignments)
        worksheet_s.write(row, 14, sub.core_assignments_progress)
        worksheet_s.write(row, 15, sub.price)
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
