from django.utils import timezone

from juntagrico.models import RecuringJob, OneTimeJob, Job

def get_current_jobs():
    return Job.objects.filter(time__gte=timezone.now()).order_by("time")


def get_current_one_time_jobs():
    return OneTimeJob.objects.filter(time__gte=timezone.now()).order_by("time")


def get_current_recuring_jobs():
    return RecuringJob.objects.filter(time__gte=timezone.now()).order_by("time")


def get_status_image(percent=0):
    if percent >= 100:
        return "circle_full.png"
    elif percent >= 75:
        return "circle_alomst_full.png"
    elif percent >= 50:
        return "circle_half.png"
    elif percent > 0:
        return "circle_almost_empty.png"
    else:
        return "circle_empty.png"


def get_status_image_text(percent=0):
    if percent >= 100:
        return "Fertig"
    elif percent >= 75:
        return "Dreiviertel"
    elif percent >= 50:
        return "Halb"
    elif percent > 0:
        return "Angefangen"
    else:
        return "Nix"
