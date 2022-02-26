from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.mailer import membernotification
from juntagrico.signals import job_canceled, job_time_changed


def job_pre_save(sender, instance, **kwargs):
    check_job_consistency(instance)
    if instance._old['canceled'] != instance.canceled and instance._old['canceled'] is False:
        job_canceled.send(sender=sender, instance=instance)
    if instance._old['time'] != instance.time:
        job_time_changed.send(sender=sender, instance=instance)


def handle_job_canceled(sender, instance, **kwargs):
    emails = set()
    for assignment in instance.assignments.all():
        emails.add(assignment.member.email)
        assignment.delete()
    instance.slots = 0
    if len(emails) > 0:
        membernotification.job_canceled(emails, instance)


def handle_job_time_changed(sender, instance, **kwargs):
    emails = set([assignment.member.email for assignment in instance.assignments.all()])
    if len(emails) > 0:
        membernotification.job_time_changed(emails, instance)


def check_job_consistency(instance):
    if instance._old['canceled'] != instance.canceled and instance._old['canceled'] is True:
        raise ValidationError(_('Abgesagte jobs koennen nicht wieder aktiviert werden'), code='invalid')
