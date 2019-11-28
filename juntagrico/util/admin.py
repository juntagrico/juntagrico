from django import forms
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from juntagrico.entity.jobs import OneTimeJob, RecuringJob


def formfield_for_coordinator(request, field_name, perm, query_function, **kwargs):
    if field_name == 'type' and request.user.has_perm(perm) and (
            not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
        kwargs['queryset'] = query_function(request.user.member)
    return kwargs


def queryset_for_coordinator(model_admin, request, field):
    qs = super(admin.ModelAdmin, model_admin).get_queryset(request)
    if request.user.has_perm('juntagrico.is_area_admin') and (
            not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
        return qs.filter(**{field: request.user.member})
    return qs


def extra_context_for_past_jobs(request, job_type, object_id, extra_context):
    job = get_object_or_404(job_type, pk=object_id)
    job_is_in_past = job.end_time() < timezone.now()
    job_is_running = job.start_time() < timezone.now()
    job_canceled = job.canceled
    job_read_only = job_canceled or job_is_running or job_is_in_past
    if job_read_only and (
            not (request.user.is_superuser or request.user.has_perm('juntagrico.can_edit_past_jobs'))):
        extra_context = extra_context or {}
        extra_context['readonly'] = True
    return extra_context


class MyHTMLWidget(forms.widgets.Widget):
    '''
    Widget that display (non-editably) arbitrary html.
    '''

    def render(self, name, value, attrs=None, renderer=None,):
        if value is None:
            return ''
        return format_html(value)


def get_job_admin_url(request, job):
    user = request.user
    if user.is_superuser or \
            user.has_perm('juntagrico.is_operations_group') or \
            job.type.activityarea.coordinator == user.member:
        if isinstance(job, OneTimeJob) and user.has_perm('juntagrico.change_onetimejob'):
            return reverse('admin:juntagrico_onetimejob_change', args=(job.id,))
        if isinstance(job, RecuringJob) and user.has_perm('juntagrico.change_recuringjob'):
            return reverse('admin:juntagrico_recuringjob_change', args=(job.id,))
    return ''
