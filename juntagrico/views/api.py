from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from juntagrico.entity.jobs import JobType
from juntagrico.templatetags.juntagrico.common import richtext


@login_required
def job_type_description(request, id):
    return HttpResponse(richtext(JobType.objects.get(id=id).description))


@login_required
def job_type_duration(request, id):
    return HttpResponse(JobType.objects.get(id=id).default_duration)
