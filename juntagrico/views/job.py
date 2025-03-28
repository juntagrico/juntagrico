from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from juntagrico.dao.jobdao import JobDao
from juntagrico.entity.jobs import Job, Assignment, JobExtra, ActivityArea
from juntagrico.entity.member import Member
from juntagrico.forms import JobSubscribeForm, EditAssignmentForm, BusinessYearForm
from juntagrico.util.admin import get_job_admin_url
from juntagrico.util.messages import alert, error_message, job_messages
from juntagrico.view_decorators import highlighted_menu


@login_required
@highlighted_menu('jobs')
def jobs(request):
    '''
    All jobs to be sorted etc.
    '''
    jobs = JobDao.get_jobs_for_current_day()
    renderdict = {
        'jobs': jobs,
        'show_all': True,
    }
    return render(request, 'jobs.html', renderdict)


@login_required
def list_data(request):
    """
    returns json data objects with jobs for datatables
    """
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = min(int(request.GET.get('length')), 1000)  # limit maximum size

    all_jobs = Job.objects.all().order_by('time')  # default order

    # filter by search
    filtered_jobs = all_jobs
    if search_time := request.GET.get('columns[0][search][value]'):
        filtered_jobs = filtered_jobs.search_time(search_time)
    if search_name := request.GET.get('columns[1][search][value]'):
        filtered_jobs = filtered_jobs.search_name(search_name)
    if search_location := request.GET.get('columns[2][search][value]'):
        filtered_jobs = filtered_jobs.search_location(search_location)
    if search_area := request.GET.get('columns[4][search][value]'):
        filtered_jobs = filtered_jobs.search_area(search_area)
    if search_value := request.GET.get('search[value]'):
        filtered_jobs = filtered_jobs.full_text_search(search_value)

    # sort results
    columns = {0: 'time'}
    order = 0
    while column := request.GET.get(f'order[{order}][column]'):
        column = columns.get(int(column))
        if column:
            direction = request.GET.get(f'order[{order}][dir]')
            if direction == 'desc':
                column = f'-{column}'
            filtered_jobs = filtered_jobs.order_by(column)
        order += 1

    # write to data
    data = []
    show_extra = JobExtra.objects.exists()
    show_core = ActivityArea.objects.filter(core=True).exists()
    for job in filtered_jobs[start:start + length]:
        data.append([
            date(job.time, 'D d.m.Y'),
            '<a href="' + reverse('job', args=[job.id]) + '" '
                'class="' + job.get_css_classes + '">' + job.type.get_name + '</a>',
            str(job.type.location),
            f"{date(job.time, 'H:i')} - {date(job.end_time(), 'H:i')}",
            job.type.activityarea.name,
            f"{job.occupied_slots}/{'&infin;' if job.infinite_slots else job.slots}",
        ])
        if show_core:
            data[-1].insert(-1, '&#10003;' if job.type.activityarea.core else '')
        if show_extra:
            data[-1].append(job.extras())

    return JsonResponse({
        'draw': draw,
        'recordsTotal': all_jobs.count(),
        'recordsFiltered': filtered_jobs.count(),
        'data': data
    })


@login_required
@highlighted_menu('jobs')
def all_jobs(request):
    '''
    All jobs to be sorted etc.
    '''
    jobs = JobDao.jobs_ordered_by_time()
    if jobs.count() > 1000:
        # use server side processing when data set is too large
        return render(request, 'juntagrico/job/list/all.html', {
            'jobs': Job.objects.none()
        })
    return render(request, 'jobs.html', {'jobs': jobs})


@login_required
@highlighted_menu('jobs')
def memberjobs(request):
    """
    Assignments of current user
    """
    member = request.user.member

    # get date range in which this member was doing assignments
    date_range = Assignment.objects.filter(member=member).aggregate(
        min_date=Min('job__time__date'), max_date=Max('job__time__date')
    )
    year_selection_form = BusinessYearForm(date_range['min_date'], date_range['max_date'], request.GET)

    # get assignments of member in selected business year
    if year_selection_form.is_valid():
        assignments = Assignment.objects.filter(
            member=member,
            job__time__date__range=year_selection_form.date_range()
        )
    else:
        assignments = Assignment.objects.none()

    return render(request, 'memberjobs.html', {
        'year_selection_form': year_selection_form,
        'assignments': assignments,
    })


@login_required
def job(request, job_id, form_class=JobSubscribeForm):
    '''
    Details for a job
    '''
    member = request.user.member
    job = get_object_or_404(Job, id=int(job_id))

    member_messages = getattr(request, 'member_messages', []) or []
    for message in messages.get_messages(request):
        member_messages.append(alert(message))

    if request.method == 'POST':
        form = form_class(member, job, request.POST)
        if form.is_valid():
            form.save()
            # redirect to same page such that refresh in the browser or back
            # button does not trigger a resubmission of the form
            return redirect('job', job_id=job_id)
    else:
        form = form_class(member, job)

    if request.method == 'POST':
        member_messages.append(error_message())

    member_messages.extend(job_messages(request, job))
    request.member_messages = member_messages
    is_job_coordinator = job.type.activityarea.coordinator == member and request.user.has_perm('juntagrico.is_area_admin')
    renderdict = {
        'job': job,
        'edit_url': get_job_admin_url(request, job),
        'form': form,
        # TODO: should also be able to contact, if is member-contact of this job or job type
        'can_contact': request.user.has_perm('juntagrico.can_send_mails') or is_job_coordinator,
        'can_edit_assignments': request.user.has_perm('juntagrico.change_assignment') or is_job_coordinator,
    }
    return render(request, 'job.html', renderdict)


@login_required
def edit_assignment(request, job_id, member_id, form_class=EditAssignmentForm, redirect_on_post=True):
    job = get_object_or_404(Job, id=int(job_id))
    # check permission
    editor = request.user.member
    is_job_coordinator = job.type.activityarea.coordinator == editor and request.user.has_perm('juntagrico.is_area_admin')
    if not (is_job_coordinator
            or request.user.has_perm('juntagrico.change_assignment')
            or request.user.has_perm('juntagrico.add_assignment')):
        raise PermissionDenied
    can_delete = is_job_coordinator or request.user.has_perm('juntagrico.delete_assignment')
    member = get_object_or_404(Member, id=int(member_id))
    success = False

    if request.method == 'POST':
        # handle submit
        form = form_class(editor, can_delete, member, job, request.POST, prefix='edit')
        if form.is_valid():
            if form.has_changed():  # don't send any notifications, if nothing was changed.
                form.save()
            success = True
        if redirect_on_post:
            if success:
                messages.success(request, mark_safe('<i class="fa-regular fa-circle-check"></i> ' +
                                                    _("Änderung gespeichert")))
            else:
                messages.error(request, _('Änderung des Einsatzes fehlgeschlagen.'))
            return redirect('job', job_id=job_id)
    else:
        form = form_class(editor, can_delete, member, job, prefix='edit')

    renderdict = {
        'member': member,
        'other_job_contacts': job.get_emails(get_member=True, exclude=[editor.email]),
        'editor': editor,
        'form': form,
        'success': success,
    }
    return render(request, 'juntagrico/job/snippets/edit_assignment.html', renderdict)
