from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, BadRequest
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST, require_GET

from juntagrico.dao.jobdao import JobDao
from juntagrico.entity.jobs import Job, Assignment, JobExtra, ActivityArea, OneTimeJob, RecuringJob, JobType
from juntagrico.entity.member import Member
from juntagrico.forms import BusinessYearForm
from juntagrico.forms.job import JobSubscribeForm, EditAssignmentForm, ConvertToRecurringJobForm
from juntagrico.util import return_to_previous_location
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
        'can_manage_jobs': request.user.member.area_access.filter(can_modify_jobs=True).exists(),
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
    context = {
        'can_manage_jobs': request.user.member.area_access.filter(can_modify_jobs=True).exists(),
    }
    if jobs.count() > 1000:
        # use server side processing when data set is too large
        return render(request, 'juntagrico/job/list/all.html', {
            'jobs': Job.objects.none(),
            **context
        })
    return render(request, 'jobs.html', {'jobs': jobs, **context})


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

    if request.method == 'POST':
        form = form_class(member, job, request.POST)
        if form.is_valid():
            form.save()
            # redirect to same page such that refresh in the browser or back
            # button does not trigger a resubmission of the form
            return redirect('job', job_id=job_id)
    else:
        form = form_class(member, job)

    permissions = job.check_if(request.user)
    is_recurring = isinstance(job.get_real_instance(), RecuringJob)
    renderdict = {
        'job': job,
        'is_recurring': is_recurring,
        'edit_url': permissions.get_edit_url(),
        'can_copy': permissions.can_copy(),
        'can_convert': permissions.can_convert(),
        'can_cancel': permissions.can_cancel(),
        # TODO: should also be able to contact, if is member-contact of this job or job type
        'can_contact': permissions.can_contact_member(),
        'can_edit_assignments': permissions.can_modify_assignments(),
        'error': request.method == 'POST',
        'form': form,
    }
    if not is_recurring:
        renderdict.update({
            'convertion_form': ConvertToRecurringJobForm(member),
            'convertion_suggestions': job.similar_job_types(5),
        })
    return render(request, 'job.html', renderdict)


@require_POST
@login_required
def convert_to_recurring(request, job_id, form_class=ConvertToRecurringJobForm, redirect_on_post=True):
    one_time_job = get_object_or_404(OneTimeJob, id=job_id)
    # check permission
    if not one_time_job.check_if(request.user).can_convert():
        raise PermissionDenied
    # evaluate form
    success = False
    form = form_class(request.user.member, request.POST)
    if form.is_valid():
        new_job = form.save(one_time_job)
        success = True
    if redirect_on_post:
        if success:
            messages.success(request, mark_safe('<i class="fa-regular fa-circle-check"></i> ' +
                                                _("Umwandlung erfolgreich")))
        else:
            messages.error(request, _('Umwandlung fehlgeschlagen'))
        return redirect('job', new_job.id if success else job_id)


@require_GET
@login_required
def convert_to_recurring_preview(request, job_id):
    member = request.user.member
    one_time_job = get_object_or_404(OneTimeJob, id=job_id)
    job_type_id = request.GET.get('job_type_id')
    if job_type_id is None or job_type_id == '':
        raise BadRequest('job type not specified')
    job_type = get_object_or_404(JobType, id=job_type_id)
    # check permission
    if not one_time_job.check_if(request.user).can_convert():
        raise PermissionDenied
    if not request.user.has_perm('juntagrico.change_onetimejob'):
        allowed_areas = member.coordinated_areas.filter(coordinator_access__can_modify_jobs=True)
        if job_type.activityarea not in allowed_areas:
            raise PermissionDenied

    return render(request, 'juntagrico/job/snippets/conversion_preview.html', {
        'one_time_job': one_time_job,
        'job_type': job_type,
    })


@require_POST
@login_required
def convert_to_one_time(request):
    job_id = request.POST.get('job_id')
    if job_id is None:
        raise BadRequest('job not specified')
    recurring_job = get_object_or_404(RecuringJob, id=job_id)
    # check permission
    if not recurring_job.check_if(request.user).can_convert():
        raise PermissionDenied
    # convert the job
    new_job = recurring_job.convert()
    messages.success(request, mark_safe('<i class="fa-regular fa-circle-check"></i> ' +
                                        _("Umwandlung erfolgreich")))
    return redirect('job', new_job.id)


@require_POST
@login_required
def cancel(request):
    job_id = request.POST.get('job_id')
    if job_id is None:
        raise BadRequest('job not specified')
    job = get_object_or_404(Job, id=int(job_id))
    # check permission
    if not job.check_if(request.user).can_cancel():
        raise PermissionDenied
    # cancel the job
    job.canceled = True
    job.save()
    return return_to_previous_location(request)


@login_required
def edit_assignment(request, job_id, member_id, form_class=EditAssignmentForm, redirect_on_post=True):
    job = get_object_or_404(Job, id=int(job_id))
    # check permission
    is_assignment_coordinator = job.check_if(request.user).is_assignment_coordinator
    if not (is_assignment_coordinator
            or request.user.has_perm('juntagrico.change_assignment')
            or request.user.has_perm('juntagrico.add_assignment')):
        raise PermissionDenied
    can_delete = is_assignment_coordinator or request.user.has_perm('juntagrico.delete_assignment')
    editor = request.user.member
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

    return render(request, 'juntagrico/job/snippets/edit_assignment.html', {
        'member': member,
        'other_job_contacts': job.get_emails(get_member=True, exclude=[editor.email]),
        'editor': editor,
        'form': form,
        'success': success,
    })
