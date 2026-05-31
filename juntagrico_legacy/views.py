from io import BytesIO

from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from xlsxwriter import Workbook

from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.forms import SubscriptionPartOrderForm
from juntagrico.util import addons, temporal, return_to_previous_location
from juntagrico.util.management import create_subscription_parts

from juntagrico.util.management_list import get_changedate
from juntagrico.view_decorators import primary_member_of_subscription

from juntagrico_legacy.util.xls import generate_excel
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
        worksheet_s.write_string(row, 6, str(sub.state_text))
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


@login_required
def subscription(request, subscription_id=None):
    '''
    Details for a subscription of a member
    '''
    member = request.user.member
    future_subscription = member.subscription_future is not None
    if subscription_id is None:
        subscription = member.subscription_current
    else:
        subscription = Subscription.objects.filter(subscriptionmembership__member=member).get(id=subscription_id)
        future_subscription = future_subscription and subscription != member.subscription_future
    end_date = temporal.end_of_next_business_year()
    renderdict = {}
    if subscription is not None:
        cancellation_date = subscription.cancellation_date
        if cancellation_date is not None and cancellation_date <= temporal.next_cancelation_date():
            end_date = temporal.end_of_business_year()
        asc = member.usable_shares_count
        share_error = subscription.share_overflow - asc < 0
        primary = subscription.primary_member.id == member.id
        can_leave = member.active_shares_count > 0 and not share_error and not primary
        renderdict.update({
            'subscription': subscription,
            'co_members': subscription.co_members(member),
            'primary': subscription.primary_member.email == member.email,
            'next_size_date': Subscription.next_size_change_date(),
            'has_extra_subscriptions': SubscriptionType.objects.is_extra().exists(),
            'sub_overview_addons': addons.config.get_sub_overviews(),
            'can_leave': can_leave,
        })
    renderdict.update({
        'no_subscription': subscription is None,
        'end_date': end_date,
        'can_order': member.can_order_subscription,
        'future_subscription': future_subscription,
        'member': request.user.member,
        'shares': request.user.member.active_shares.count(),
        'shares_unpaid': request.user.member.share_set.filter(paid_date=None).count(),
    })
    return render(request, 'subscription.html', renderdict)


@primary_member_of_subscription
def subscription_change(request, subscription_id):
    '''
    change a subscription
    '''
    subscription = get_object_or_404(Subscription, id=subscription_id)
    renderdict = {
        'subscription': subscription,
        'member': request.user.member,
        'next_cancel_date': temporal.next_cancelation_date(),
        'next_business_year': temporal.start_of_next_business_year(),
        'sub_change_addons': addons.config.get_sub_changes(),
    }
    return render(request, 'subscription_change.html', renderdict)


@primary_member_of_subscription
def size_change(request, subscription_id):
    """
    change the size of a subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        form = SubscriptionPartOrderForm(subscription, request.POST)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return return_to_previous_location(request)
    else:
        form = SubscriptionPartOrderForm()
    renderdict = {
        'form': form,
        'subscription': subscription,
        'hours_used': Config.assignment_unit() == 'HOURS',
        'next_cancel_date': temporal.next_cancelation_date(),
        'parts_order_allowed': not subscription.canceled,
        'can_change_part': SubscriptionType.objects.can_change()
    }
    return render(request, 'size_change.html', renderdict)


@primary_member_of_subscription
def extra_change(request, subscription_id):
    """
        change an extra subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        form = SubscriptionPartOrderForm(subscription, request.POST, extra=True)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return return_to_previous_location(request)
    else:
        form = SubscriptionPartOrderForm(extra=True)
    renderdict = {
        'form': form,
        'extras': subscription.active_and_future_extra_subscriptions.all(),
        'subscription': subscription,
        'sub_id': subscription_id,
        'extra_order_allowed': not subscription.canceled,
    }
    return render(request, 'extra_change.html', renderdict)
