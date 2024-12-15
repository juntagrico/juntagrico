from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.entity.jobs import Job
from juntagrico.entity.member import Member
from juntagrico.forms import JobSubscribeForm, EditAssignmentForm
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
@highlighted_menu('jobs')
def all_jobs(request):
    '''
    All jobs to be sorted etc.
    '''
    jobs = JobDao.jobs_ordered_by_time()
    renderdict = {
        'jobs': jobs
    }

    return render(request, 'jobs.html', renderdict)


@login_required
@highlighted_menu('jobs')
def memberjobs(request):
    '''
    All jobs of current user
    '''
    member = request.user.member
    allassignments = AssignmentDao.assignments_for_member(member)
    renderdict = {
        'assignments': allassignments,
    }
    return render(request, 'memberjobs.html', renderdict)


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
