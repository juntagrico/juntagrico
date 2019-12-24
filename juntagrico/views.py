from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.deliverydao import DeliveryDao
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.jobextradao import JobExtraDao
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import Job, Assignment, ActivityArea
from juntagrico.entity.member import Member
from juntagrico.forms import MemberProfileForm, PasswordForm
from juntagrico.mailer import FormEmails, MemberNotification, AdminNotification
from juntagrico.util import addons
from juntagrico.util.admin import get_job_admin_url
from juntagrico.util.mailer import append_attachements
from juntagrico.util.management import password_generator, cancel_share
from juntagrico.util.messages import home_messages, job_messages
from juntagrico.util.temporal import next_membership_end_date


def get_page_dict(request):
    return {
        'view_name': request.resolver_match.view_name.replace('.', '-'),
    }


def get_menu_dict(request):
    member = request.user.member
    next_jobs = JobDao.upcomming_jobs_for_member(member)

    required_assignments = 0
    if member.subscription is not None:
        partner_assignments = []
        for subscription_member in member.subscription.recipients_all:
            if subscription_member == member:
                continue
            partner_assignments.extend(
                AssignmentDao.assignments_for_member_current_business_year(subscription_member))

        userassignments = AssignmentDao.assignments_for_member_current_business_year(
            member)
        required_assignments = member.subscription.required_assignments
    else:
        partner_assignments = []
        userassignments = []

    userassignments_total = int(sum(a.amount for a in userassignments))
    userassignemnts_core = int(
        sum(a.amount for a in userassignments if a.is_core()))
    partner_assignments_total = int(sum(a.amount for a in partner_assignments))
    partner_assignments_core = int(
        sum(a.amount for a in partner_assignments if a.is_core()))
    assignmentsrange = list(range(
        0, max(required_assignments, userassignments_total + partner_assignments_total)))

    depot_admin = DepotDao.depots_for_contact(request.user.member)
    area_admin = ActivityAreaDao.areas_by_coordinator(request.user.member)
    menu_dict = get_page_dict(request)
    menu_dict.update({
        'user': request.user,
        'assignmentsrange': assignmentsrange,
        'userassignments_bound': userassignments_total,
        'userassignemnts_core_bound': userassignemnts_core,
        'partner_assignments_bound': userassignments_total + partner_assignments_total,
        'partner_assignments_core_bound': userassignments_total + partner_assignments_core,
        'next_jobs': next_jobs,
        'can_filter_members': request.user.has_perm('juntagrico.can_filter_members'),
        'can_filter_subscriptions': request.user.has_perm('juntagrico.can_filter_subscriptions'),
        'can_send_mails': request.user.has_perm('juntagrico.can_send_mails'),
        'operation_group': request.user.has_perm('juntagrico.is_operations_group'),
        'has_extra_subscriptions': ExtraSubscriptionCategoryDao.all_categories_ordered().count() > 0,
        'depot_admin': depot_admin,
        'area_admin': area_admin,
        'show_core': ActivityAreaDao.all_core_areas().count() > 0,
        'show_extras': JobExtraDao.all_job_extras().count() > 0,
        'show_deliveries': len(DeliveryDao.deliveries_by_subscription(request.user.member.subscription)) > 0,
        'admin_menus': addons.config.get_admin_menus(),
        'admin_subscription_menus': addons.config.get_admin_subscription_menu(),
        'user_menus': addons.config.get_user_menus(),
        'messages': [],

    })
    return menu_dict


@login_required
def home(request):
    '''
    Overview on juntagrico
    '''

    next_jobs = set(JobDao.get_current_jobs()[:7])
    pinned_jobs = set(JobDao.get_pinned_jobs())
    next_promotedjobs = set(JobDao.get_promoted_jobs())
    renderdict = get_menu_dict(request)
    renderdict['messages'].extend(home_messages(request))
    renderdict.update({
        'jobs': sorted(next_jobs.union(pinned_jobs).union(next_promotedjobs), key=lambda job: job.time),
        'areas': ActivityAreaDao.all_visible_areas_ordered(),
    })

    return render(request, 'home.html', renderdict)


@login_required
def job(request, job_id):
    '''
    Details for a job
    '''
    member = request.user.member
    job = get_object_or_404(Job, id=int(job_id))

    if request.method == 'POST':
        num = request.POST.get('jobs')
        # adding participants
        amount = 1
        if Config.assignment_unit() == 'ENTITY':
            amount = job.multiplier
        elif Config.assignment_unit() == 'HOURS':
            amount = job.multiplier * job.type.duration
        add = int(num)
        for i in range(add):
            assignment = Assignment.objects.create(
                member=member, job=job, amount=amount)
        for extra in job.type.job_extras_set.all():
            if request.POST.get('extra' + str(extra.extra_type.id)) == str(extra.extra_type.id):
                assignment.job_extras.add(extra)
        assignment.save()

        MemberNotification.job_signup([member.email], job)
        # redirect to same page such that refresh in the browser or back
        # button does not trigger a resubmission of the form
        return redirect('job', job_id=job_id)

    all_participants = MemberDao.members_by_job(job)
    number_of_participants = len(all_participants)
    unique_participants = all_participants.annotate(
        assignment_for_job=Count('id')).distinct()

    participants_summary = []
    emails = []
    for member in unique_participants:
        name = '{} {}'.format(member.first_name, member.last_name)
        if member.assignment_for_job == 2:
            name += _(' (mit einer weiteren Person)')
        elif member.assignment_for_job > 2:
            name += _(' (mit {} weiteren Personen)').format(member.assignment_for_job - 1)
        contact_url = '/my/contact/member/{}/{}/'.format(member.id, job_id)
        extras = []
        for assignment in AssignmentDao.assignments_for_job_and_member(job.id, member):
            for extra in assignment.job_extras.all():
                extras.append(extra.extra_type.display_full)
        reachable = member.reachable_by_email is True or request.user.is_staff or job.type.activityarea.coordinator == member
        participants_summary.append(
            (name, None, contact_url, reachable, ' '.join(extras)))
        emails.append(member.email)

    slotrange = list(range(0, job.slots))
    allowed_additional_participants = list(
        range(1, job.slots - number_of_participants + 1))
    job_fully_booked = len(allowed_additional_participants) == 0
    job_is_in_past = job.end_time() < timezone.now()
    job_is_running = job.start_time() < timezone.now()
    job_canceled = job.canceled
    can_subscribe = not (
        job_fully_booked or job_is_in_past or job_is_running or job_canceled)

    renderdict = get_menu_dict(request)
    renderdict['messages'].extend(job_messages(request, job))
    renderdict.update({
        'admin': request.user.is_staff or job.type.activityarea.coordinator == member,
        'emails': '\n'.join(emails),
        'number_of_participants': number_of_participants,
        'participants_summary': participants_summary,
        'job': job,
        'slotrange': slotrange,
        'allowed_additional_participants': allowed_additional_participants,
        'can_subscribe': can_subscribe,
        'edit_url': get_job_admin_url(request, job)
    })
    return render(request, 'job.html', renderdict)


@login_required
def depot(request, depot_id):
    '''
    Details for a Depot
    '''
    depot = get_object_or_404(Depot, id=int(depot_id))

    renderdict = get_menu_dict(request)
    renderdict.update({
        'depot': depot,
        'requires_map': depot.has_geo
    })
    return render(request, 'depot.html', renderdict)


@login_required
def areas(request):
    '''
    Details for all areas a member can participate
    '''
    member = request.user.member
    my_areas = []
    for area in ActivityAreaDao.all_visible_areas():
        my_areas.append({
            'name': area.name,
            'checked': member in area.members.all(),
            'id': area.id,
            'core': area.core,
            'coordinator': area.coordinator,
            'email': area.email
        })

    renderdict = get_menu_dict(request)
    renderdict.update({
        'areas': my_areas,
        'menu': {'area': 'active'},
    })
    return render(request, 'areas.html', renderdict)


@login_required
def memberjobs(request):
    '''
    All jobs of current user
    '''
    member = request.user.member
    allassignments = AssignmentDao.assignments_for_member(member)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'assignments': allassignments,
        'menu': {'jobs': 'active'},
    })
    return render(request, 'memberjobs.html', renderdict)


@login_required
def show_area(request, area_id):
    '''
    Details for an area
    '''
    area = get_object_or_404(ActivityArea, id=int(area_id))
    job_types = JobTypeDao.types_by_area(area_id)
    otjobs = JobDao.get_current_one_time_jobs().filter(activityarea=area_id)
    rjobs = JobDao.get_current_recuring_jobs().filter(type__in=job_types)
    jobs = list(rjobs)
    if len(otjobs) > 0:
        jobs.extend(list(otjobs))
        jobs.sort(key=lambda job: job.time)
    area_checked = request.user.member in area.members.all()
    renderdict = get_menu_dict(request)
    renderdict.update({
        'area': area,
        'jobs': jobs,
        'area_checked': area_checked,
    })
    return render(request, 'area.html', renderdict)


@login_required
def area_join(request, area_id):
    new_area = get_object_or_404(ActivityArea, id=int(area_id))
    member = request.user.member
    new_area.members.add(member)
    AdminNotification.member_joined_activityarea(new_area, member)
    new_area.save()
    return HttpResponse('')


@login_required
def area_leave(request, area_id):
    old_area = get_object_or_404(ActivityArea, id=int(area_id))
    member = request.user.member
    old_area.members.remove(member)
    AdminNotification.member_left_activityarea(old_area, member)
    old_area.save()
    return HttpResponse('')


@login_required
def jobs(request):
    '''
    All jobs to be sorted etc.
    '''
    renderdict = get_menu_dict(request)

    jobs = JobDao.get_jobs_for_current_day()
    renderdict.update({
        'jobs': jobs,
        'show_all': True,
        'menu': {'jobs': 'active'},
    })

    return render(request, 'jobs.html', renderdict)


@login_required
def all_jobs(request):
    '''
    All jobs to be sorted etc.
    '''
    renderdict = get_menu_dict(request)
    jobs = JobDao.jobs_ordered_by_time()
    renderdict.update({
        'jobs': jobs,
        'menu': {'jobs': 'active'},
    })

    return render(request, 'jobs.html', renderdict)


@login_required
def deliveries(request):
    '''
    All deliveries to be sorted etc.
    '''
    renderdict = get_menu_dict(request)
    deliveries = DeliveryDao.deliveries_by_subscription(
        request.user.member.subscription)
    renderdict.update({
        'deliveries': deliveries,
        'menu': {'deliveries': 'active'},
    })

    return render(request, 'deliveries.html', renderdict)


@login_required
def contact(request):
    '''
    contact form
    '''
    member = request.user.member
    is_sent = False

    if request.method == 'POST':
        # send mail to organisation
        FormEmails.contact(request.POST.get('subject'), request.POST.get('message'), member, request.POST.get('copy'))
        is_sent = True

    renderdict = get_menu_dict(request)
    renderdict.update({
        'usernameAndEmail': member.first_name + ' ' + member.last_name + '<' + member.email + '>',
        'is_sent': is_sent,
        'menu': {'contact': 'active'},
    })
    return render(request, 'contact.html', renderdict)


@login_required
def contact_member(request, member_id, job_id):
    '''
    member contact form
    '''
    member = request.user.member
    contact_member = get_object_or_404(Member, id=int(member_id))
    is_sent = False

    if request.method == 'POST':
        # send mail to member
        attachments = []
        append_attachements(request, attachments)
        FormEmails.contact_member(request.POST.get('subject'), request.POST.get('message'), member, contact_member,
                                  request.POST.get('copy'), attachments)
        is_sent = True
    job = JobDao.job_by_id(job_id)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'admin': request.user.is_staff or job.type.activityarea.coordinator == member,
        'usernameAndEmail': member.first_name + ' ' + member.last_name + '<' + member.email + '>',
        'member_id': member_id,
        'member_name': contact_member.first_name + ' ' + contact_member.last_name,
        'is_sent': is_sent,
        'job_id': job_id
    })
    return render(request, 'contact_member.html', renderdict)


@login_required
def profile(request):
    success = False
    member = request.user.member
    if request.method == 'POST':
        memberform = MemberProfileForm(request.POST, instance=member)
        if memberform.is_valid():
            # set all fields of user
            member.first_name = memberform.cleaned_data['first_name']
            member.last_name = memberform.cleaned_data['last_name']
            member.email = memberform.cleaned_data['email']
            member.addr_street = memberform.cleaned_data['addr_street']
            member.addr_zipcode = memberform.cleaned_data['addr_zipcode']
            member.addr_location = memberform.cleaned_data['addr_location']
            member.phone = memberform.cleaned_data['phone']
            member.mobile_phone = memberform.cleaned_data['mobile_phone']
            member.iban = memberform.cleaned_data['iban']
            member.reachable_by_email = memberform.cleaned_data['reachable_by_email']
            member.save()
            success = True
    else:
        memberform = MemberProfileForm(instance=member)
    renderdict = get_menu_dict(request)
    renderdict.update({
        'memberform': memberform,
        'success': success,
        'member': member,
        'menu': {'personalInfo': 'active'},
    })
    return render(request, 'profile.html', renderdict)


@login_required
def cancel_membership(request):
    member = request.user.member
    if request.method == 'POST':
        now = timezone.now().date()
        end_date = next_membership_end_date().date()
        message = request.POST.get('message')
        member = request.user.member
        member.canceled = True
        member.end_date = end_date
        member.cancelation_date = now
        if member.is_cooperation_member:
            AdminNotification.member_canceled(member, end_date, message)
        else:
            member.inactive = True

        member.save()
        for share in member.active_shares:
            cancel_share(share, now, end_date)
        return redirect('profile')

    missing_iban = member.iban == ''
    coop_member = member.is_cooperation_member
    asc = member.active_shares_count
    sub = member.subscription
    f_sub = member.future_subscription
    future_active = f_sub is not None and f_sub.state == 'active' and f_sub.state == 'waiting'
    current_active = sub is not None and sub.state == 'active' and sub.state == 'waiting'
    future = future_active and f_sub.share_overflow - asc < 0
    current = current_active and sub.share_overflow - asc < 0
    share_error = future or current
    can_cancel = not coop_member or (not missing_iban and not share_error)

    renderdict = get_menu_dict(request)
    renderdict.update({
        'coop_member': coop_member,
        'end_date': next_membership_end_date(),
        'member': member,
        'can_cancel': can_cancel,
        'missing_iban': missing_iban,
    })
    return render(request, 'cancelmembership.html', renderdict)


@login_required
def send_confirm(request):
    MemberNotification.email_confirmation(request.user.member)
    renderdict = get_menu_dict(request)
    return render(request, 'info/confirmation_sent.html', renderdict)


@login_required
def info_unpaid_shares(request):
    renderdict = get_menu_dict(request)
    return render(request, 'info/unpaid_shares.html', renderdict)


@login_required
def change_password(request):
    success = False
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            success = True
    else:
        form = PasswordForm()

    renderdict = get_menu_dict(request)
    renderdict.update({
        'form': form,
        'success': success
    })
    return render(request, 'password.html', renderdict)


def new_password(request):
    sent = False
    if request.method == 'POST':
        sent = True
        member = MemberDao.member_by_email(request.POST.get('username'))
        if member is not None:
            pw = password_generator()
            member.user.set_password(pw)
            member.user.save()
            MemberNotification.reset_password(member.email, pw)

    renderdict = get_page_dict(request)
    renderdict.update({
        'sent': sent
    })
    return render(request, 'newpassword.html', renderdict)


def logout_view(request):
    auth.logout(request)
    return redirect('home')


def cookies(request):
    return render(request, 'cookie.html', {})
