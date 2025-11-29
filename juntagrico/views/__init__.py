from datetime import timedelta

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone

from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.deliverydao import DeliveryDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, Job
from juntagrico.entity.member import Member
from juntagrico.forms import MemberProfileForm, PasswordForm, NonCoopMemberCancellationForm, \
    CoopMemberCancellationForm, AreaDescriptionForm
from juntagrico.mailer import adminnotification
from juntagrico.mailer import append_attachements
from juntagrico.mailer import formemails
from juntagrico.mailer import membernotification
from juntagrico.signals import area_joined, area_left, canceled
from juntagrico.util.temporal import next_membership_end_date
from juntagrico.view_decorators import highlighted_menu
from juntagrico.config import Config


@login_required
def home(request):
    '''
    Overview on juntagrico
    '''
    # collect upcoming jobs
    start = timezone.now()
    jobs_base = Job.objects.filter(canceled=False, time__gte=start).with_free_slots()
    # collect jobs that always show
    # avoiding LIMIT in IN-subquery to support mysql https://dev.mysql.com/doc/refman/8.4/en/subquery-restrictions.html
    pinned_jobs = jobs_base.filter(pinned=True)
    promoted_jobs = jobs_base.by_type_name(Config.promoted_job_types()).next(Config.promoted_jobs_amount())
    show_job_ids = set(pinned_jobs.values_list('id', flat=True)) | set(promoted_jobs.values_list('id', flat=True))
    show_jobs_count = len(show_job_ids)
    # fill with future jobs of next x days or until max
    remaining_to_max = Config.jobs_frontpage_max_amount() - show_jobs_count
    if remaining_to_max > 0:
        end = start + timedelta(Config.jobs_frontpage_range_days())
        next_jobs = jobs_base.exclude(id__in=show_job_ids).filter(time__lte=end).next(remaining_to_max)
        # if next x days are not enough to fill to min, load enough to fill to min
        remaining_to_min = Config.jobs_frontpage_min_amount() - show_jobs_count - next_jobs.count()
        if remaining_to_min > 0:
            next_jobs = jobs_base.exclude(id__in=show_job_ids).next(remaining_to_min)
        show_job_ids |= set(next_jobs.values_list('id', flat=True))

    return render(request, 'home.html', {
        'jobs': Job.objects.filter(id__in=show_job_ids).order_by('time'),
        'can_manage_jobs': request.user.member.area_access.filter(can_modify_jobs=True).exists(),
        'areas': ActivityAreaDao.all_visible_areas_ordered(),
    })


@login_required
def depot_landing(request):
    subscription = request.user.member.subscription_current or request.user.member.subscription_future
    if subscription:
        return depot(request, subscription.depot_id)
    return redirect('home')


@login_required
def depot(request, depot_id):
    '''
    Details for a Depot
    '''
    depot = get_object_or_404(Depot, id=int(depot_id))
    renderdict = {
        'depot': depot,
        'show_access': request.user.member.subscriptionmembership_set.filter(
            subscription__depot=depot).count() > 0
    }
    return render(request, 'depot.html', renderdict)


@login_required
@highlighted_menu('area')
def areas(request):
    '''
    List all areas a member can participate in
    '''
    return render(request, 'areas.html', {
        'areas': ActivityArea.objects.filter(hidden=False).order_by('-core', 'name'),
        'coordinated_areas': request.user.member.coordinated_areas.all(),
    })


@login_required
def show_area(request, area_id):
    '''
    Details for an area
    '''
    area = get_object_or_404(ActivityArea, id=int(area_id))
    edit_form = None
    access = request.user.member.area_access.filter(area=area).first()
    if access and access.can_modify_area:
        if request.method == 'POST':
            edit_form = AreaDescriptionForm(request.POST, instance=area)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('area', area_id=area_id)
        else:
            edit_form = AreaDescriptionForm(instance=area)

    job_types = JobTypeDao.types_by_area(area_id)
    otjobs = JobDao.get_current_one_time_jobs().filter(activityarea=area_id)
    rjobs = JobDao.get_current_recuring_jobs().filter(type__in=job_types)
    jobs = list(rjobs)
    if len(otjobs) > 0:
        jobs.extend(list(otjobs))
        jobs.sort(key=lambda job: job.time)
    area_checked = request.user.member.areas.filter(pk=area.pk).exists()

    renderdict = {
        'area': area,
        'jobs': jobs,
        'area_checked': area_checked,
        'edit_form': edit_form,
        'can_view_member': access and access.can_view_member,
        'can_manage_jobs': access and access.can_modify_jobs
    }
    return render(request, 'area.html', renderdict)


@login_required
def area_join(request, area_id):
    new_area = get_object_or_404(ActivityArea, id=int(area_id))
    member = request.user.member
    new_area.members.add(member)
    area_joined.send(ActivityArea, area=new_area, member=member)
    adminnotification.member_joined_activityarea(new_area, member)
    new_area.save()
    return HttpResponse()


@login_required
def area_leave(request, area_id):
    old_area = get_object_or_404(ActivityArea, id=int(area_id))
    member = request.user.member
    old_area.members.remove(member)
    area_left.send(ActivityArea, area=old_area, member=member)
    adminnotification.member_left_activityarea(old_area, member)
    old_area.save()
    return HttpResponse()


@login_required
@highlighted_menu('deliveries')
def deliveries(request):
    '''
    All deliveries to be sorted etc.
    '''
    deliveries = DeliveryDao.deliveries_by_subscription(
        request.user.member.subscription_current)
    renderdict = {
        'deliveries': deliveries
    }
    return render(request, 'deliveries.html', renderdict)


@login_required
@highlighted_menu('contact')
def contact(request):
    '''
    contact form
    '''
    member = request.user.member
    is_sent = False

    if request.method == 'POST':
        # send mail to organisation
        formemails.contact(request.POST.get('subject'), request.POST.get('message'), member, request.POST.get('copy'))
        is_sent = True
    renderdict = {
        'usernameAndEmail': member.first_name + ' ' + member.last_name + ' <' + member.email + '>',
        'is_sent': is_sent
    }
    return render(request, 'contact.html', renderdict)


@login_required
def contact_member(request, member_id):
    '''
    member contact form
    '''
    sender = request.user.member
    receiver = get_object_or_404(Member, id=int(member_id))
    if not sender.can_contact(receiver):
        raise PermissionDenied()

    enable_attachments = request.user.has_perm('juntagrico.can_email_attachments')
    back_url = request.META.get('HTTP_REFERER') or reverse('home')

    is_sent = False
    if request.method == 'POST':
        # send mail to member
        back_url = request.POST.get('back_url')
        files = []
        if enable_attachments:
            append_attachements(request, files)
        formemails.contact_member(request.POST.get('subject'), request.POST.get('message'), sender, receiver,
                                  request.POST.get('copy'), files)
        is_sent = True

    return render(request, 'contact_member.html', {
        'enable_attachments': enable_attachments,
        'usernameAndEmail': sender.first_name + ' ' + sender.last_name + '<' + sender.email + '>',
        'member_id': member_id,
        'member_name': receiver.first_name + ' ' + receiver.last_name,
        'is_sent': is_sent,
        'back_url': back_url
    })


@login_required
@highlighted_menu('membership')
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
    renderdict = {
        'memberform': memberform,
        'success': success,
        'member': member
    }
    return render(request, 'profile.html', renderdict)


@login_required
def cancel_membership(request):
    member = request.user.member
    # Check if membership can be canceled
    asc = member.usable_shares_count
    sub = member.subscription_current
    f_sub = member.subscription_future
    future_active = f_sub is not None and not f_sub.canceled
    current_active = sub is not None and not sub.canceled
    future = future_active and f_sub.share_overflow - asc < 0
    current = current_active and sub.share_overflow - asc < 0
    share_error = future or current
    can_cancel = not share_error and not future_active and not current_active
    # considering unpaid shares as well, as they might have been paid but not yet updated in the system.
    # Then IBAN is needed to pay it back.
    coop_member = member.usable_shares_count > 0
    if coop_member:
        form_type = CoopMemberCancellationForm
    else:
        form_type = NonCoopMemberCancellationForm
    if can_cancel and request.method == 'POST':
        form = form_type(request.POST, instance=member)
        if form.is_valid():
            form.save()
            canceled.send(Member, instance=form.instance, message=form.cleaned_data.get('message'))
            return redirect('profile')
    else:
        form = form_type(instance=member)
    renderdict = {
        'coop_member': coop_member,
        'end_date': next_membership_end_date(),
        'member': member,
        'can_cancel': can_cancel,
        'share_error': share_error,
        'form': form
    }
    return render(request, 'cancelmembership.html', renderdict)


@login_required
def send_confirm(request):
    membernotification.email_confirmation(request.user.member)
    return render(request, 'info/confirmation_sent.html', {})


@login_required
def info_unpaid_shares(request):
    return render(request, 'info/unpaid_shares.html', {})


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

    renderdict = {
        'form': form,
        'success': success
    }
    return render(request, 'password.html', renderdict)


def logout_view(request):
    auth.logout(request)
    return redirect('home')


def cookies(request):
    return render(request, 'cookie.html', {})


def i18njs(request):
    return render(request, 'js/i18n.js', {}, content_type='application/javascript')
