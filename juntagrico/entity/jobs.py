# encoding: utf-8

from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from polymorphic.models import PolymorphicModel

from juntagrico.dao.assignmentdao import AssignmentDao

from juntagrico.util.jobs import *
from juntagrico.util.temporal import *
from juntagrico.config import Config
from juntagrico.mailer import *


class ActivityArea(models.Model):

    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, default='')
    email = models.EmailField(null=True, blank=True)
    core = models.BooleanField(_('Kernbereich'), default=False)
    hidden = models.BooleanField(_('versteckt'), default=False)
    coordinator = models.ForeignKey('Member', on_delete=models.PROTECT)
    members = models.ManyToManyField(
        'Member', related_name='areas', blank=True)
    show_coordinator_phonenumber = models.BooleanField(
        _('Koordinator Tel Nr Veröffentlichen'), default=False)

    def __str__(self):
        return '%s' % self.name

    def contact(self):
        if self.show_coordinator_phonenumber is True:
            return self.coordinator.phone + '   ' + self.coordinator.mobile_phone
        elif self.email is not None:
            return self.email
        else:
            return self.coordinator.email

    class Meta:
        verbose_name = _('Tätigkeitsbereich')
        verbose_name_plural = _('Tätigkeitsbereiche')
        permissions = (
            ('is_area_admin', _('Benutzer ist TätigkeitsbereichskoordinatorIn')),)


class JobExtraType(models.Model):
    '''
    Types of extras which a job type might need or can have
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    display_empty = models.CharField(
        _('Icon für fehlendes Extra'), max_length=1000, blank=False, null=False)
    display_full = models.CharField(
        _('Icon für Extra'), max_length=1000, blank=False, null=False)

    class Meta:
        verbose_name = _('JobExtraTyp')
        verbose_name_plural = _('JobExtraTypen')


class JobExtra(models.Model):
    '''
    Actual Extras mapping
    '''
    recuring_type = models.ForeignKey('JobType', related_name='job_extras_set', null=True,
                                      blank=True,
                                      on_delete=models.PROTECT)
    onetime_type = models.ForeignKey('OneTimeJob', related_name='job_extras_set', null=True,
                                     blank=True,
                                     on_delete=models.PROTECT)
    extra_type = models.ForeignKey('JobExtraType', related_name='job_types_set', null=False,
                                   blank=False,
                                   on_delete=models.PROTECT)
    per_member = models.BooleanField(
        _('jeder kann Extra auswählen'), default=False)

    def empty(self, assignment_set):
        ids = [assignment.id for assignment in assignment_set]
        return self.assignments.filter(id__in=ids).count() == 0

    @property
    def type(self):
        if recuring_type is not None:
            return recuring_type
        return onetime_type

    class Meta:
        verbose_name = _('JobExtra')
        verbose_name_plural = _('JobExtras')


class AbstractJobType(models.Model):
    '''
    Abstract type of job.
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    displayed_name = models.CharField(
        _('Angezeigter Name'), max_length=100, blank=True, null=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, default='')
    activityarea = models.ForeignKey(ActivityArea, on_delete=models.PROTECT)
    duration = models.PositiveIntegerField(_('Dauer in Stunden'))
    location = models.CharField('Ort', max_length=100, default='')

    def __str__(self):
        return '%s - %s' % (self.activityarea, self.get_name)

    @property
    def get_name(self):
        if self.displayed_name is not None and self.displayed_name != '':
            return self.displayed_name
        return self.name

    class Meta:
        verbose_name = _('AbstractJobart')
        verbose_name_plural = _('AbstractJobarten')
        abstract = True


class JobType(AbstractJobType):
    '''
    Recuring type of job. do not add field here do it in the parent
    '''

    class Meta:
        verbose_name = _('Jobart')
        verbose_name_plural = _('Jobarten')


class Job(PolymorphicModel):
    slots = models.PositiveIntegerField(_('Plaetze'))
    time = models.DateTimeField()
    multiplier = models.PositiveIntegerField(
        Config.vocabulary('assignment')+' vielfaches', default=1)
    pinned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(
        _('Reminder verschickt'), default=False)
    canceled = models.BooleanField(_('abgesagt'), default=False)
    old_canceled = None
    old_time = None

    @property
    def type(self):
        raise NotImplementedError

    def __str__(self):
        return _('Job #%s') % self.id

    def weekday_name(self):
        day = self.time.isoweekday()
        return weekday_short(day, 2)

    def time_stamp(self):
        return int(time.mktime(self.time.timetuple()) * 1000)

    def free_slots(self):
        if not (self.slots is None):
            return self.slots - self.occupied_places()
        else:
            return 0

    def end_time(self):
        return self.time + timezone.timedelta(hours=self.type.duration)

    def start_time(self):
        return self.time

    def occupied_places(self):
        return self.assignment_set.count()

    def get_status_percentage(self):
        assignments = AssignmentDao.assignments_for_job(self.id)
        if self.slots < 1:
            return get_status_image(100)
        return get_status_image(assignments.count() * 100 / self.slots)

    def is_core(self):
        return self.type.activityarea.core

    def extras(self):
        extras_result = []
        for extra in self.type.job_extras_set.all():
            if extra.empty(self.assignment_set.all()):
                extras_result.append(extra.extra_type.display_empty)
            else:
                extras_result.append(extra.extra_type.display_full)
        return ' '.join(extras_result)

    def empty_per_job_extras(self):
        extras_result = []
        for extra in self.type.job_extras_set.filter(per_member=False):
            if extra.empty(self.assignment_set.all()):
                extras_result.append(extra)
        return extras_result

    def full_per_job_extras(self):
        extras_result = []
        for extra in self.type.job_extras_set.filter(per_member=False):
            if not extra.empty(self.assignment_set.all()):
                extras_result.append(extra)
        return extras_result

    def per_member_extras(self):
        return self.type.job_extras_set.filter(per_member=True)

    def clean(self):
        if self.old_canceled != self.canceled and self.old_canceled is True:
            raise ValidationError(
                _('Abgesagte jobs koennen nicht wieder aktiviert werden'), code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_canceled != instance.canceled and instance.old_canceled is False:
            assignments = AssignmentDao.assignments_for_job(instance.id)
            emails = set()
            for assignment in assignments:
                emails.add(assignment.member.email)
            instance.slots = 0
            if len(emails) > 0:
                send_job_canceled(emails, instance)
        if instance.old_time != instance.time:
            assignments = AssignmentDao.assignments_for_job(instance.id)
            emails = set()
            for assignment in assignments:
                emails.add(assignment.member.email)
            if len(emails) > 0:
                send_job_time_changed(emails, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_time = instance.time
        instance.old_canceled = instance.canceled
        if instance.canceled:
            assignments = AssignmentDao.assignments_for_job(instance.id)
            assignments.delete()

    class Meta:
        verbose_name = _('AbstractJob')
        verbose_name_plural = _('AbstractJobs')


class RecuringJob(Job):
    type = models.ForeignKey(JobType, on_delete=models.PROTECT)

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')


class OneTimeJob(Job, AbstractJobType):
    '''
    One time job. Do not add Field here do it in the Parent class
    '''

    @property
    def type(self):
        return self

    def __str__(self):
        return '%s - %s' % (self.activityarea, self.get_name)

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        Job.post_init(sender, instance)

    class Meta:
        verbose_name = _('EinzelJob')
        verbose_name_plural = _('EinzelJobs')


class Assignment(models.Model):
    '''
    Single assignment (work unit).
    '''
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.PROTECT)
    core_cache = models.BooleanField(_('Kernbereich'), default=False)
    job_extras = models.ManyToManyField(
        JobExtra, related_name='assignments', blank=True)
    amount = models.FloatField(_('Wert'))

    def __str__(self):
        return '%s #%s' % (Config.vocabulary('assignment'), self.id)

    def time(self):
        return self.job.time

    def is_core(self):
        return self.job.type.activityarea.core

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        instance.core_cache = instance.is_core()

    class Meta:
        verbose_name = Config.vocabulary('assignment')
        verbose_name_plural = Config.vocabulary('assignment_pl')
