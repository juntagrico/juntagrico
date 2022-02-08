from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import time
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity import JuntagricoBaseModel, JuntagricoBasePoly, absolute_url
from juntagrico.entity.contact import get_emails, MemberContact, Contact
from juntagrico.entity.location import Location
from juntagrico.lifecycle.job import check_job_consistency
from juntagrico.util.temporal import weekday_short


@absolute_url(name='area')
class ActivityArea(JuntagricoBaseModel):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, default='')
    core = models.BooleanField(_('Kernbereich'), default=False)
    hidden = models.BooleanField(
        _('versteckt'), default=False,
        help_text=_('Nicht auf der "Tätigkeitsbereiche"-Seite anzeigen. Einsätze bleiben sichtbar.'))
    coordinator = models.ForeignKey('Member', on_delete=models.PROTECT, verbose_name=_('KoordinatorIn'))
    members = models.ManyToManyField(
        'Member', related_name='areas', blank=True, verbose_name=Config.vocabulary('member_pl'))
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)
    auto_add_new_members = models.BooleanField(_('Standard Tätigkeitesbereich für neue Benutzer'), default=False,
                                               help_text=_(
                                                   'Neue Benutzer werden automatisch zu diesem Tätigkeitsbereich hinzugefügt.'))

    contact_set = GenericRelation(Contact)

    def __str__(self):
        return '%s' % self.name

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        return MemberContact(member=self.coordinator),  # last resort: show area admin as contact

    def get_emails(self):
        return get_emails(self.contact_set, lambda: [self.coordinator.email])

    class Meta:
        verbose_name = _('Tätigkeitsbereich')
        verbose_name_plural = _('Tätigkeitsbereiche')
        ordering = ['sort_order']
        permissions = (
            ('is_area_admin', _('Benutzer ist TätigkeitsbereichskoordinatorIn')),)


class JobExtraType(JuntagricoBaseModel):
    '''
    Types of extras which a job type might need or can have
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    display_empty = models.CharField(
        _('Icon für fehlendes Extra'), max_length=1000, blank=False, null=False)
    display_full = models.CharField(
        _('Icon für Extra'), max_length=1000, blank=False, null=False)

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        verbose_name = _('JobExtraTyp')
        verbose_name_plural = _('JobExtraTypen')


class JobExtra(JuntagricoBaseModel):
    '''
    Actual Extras mapping
    '''
    recuring_type = models.ForeignKey('JobType', related_name='job_extras_set', null=True, blank=True,
                                      on_delete=models.PROTECT)
    onetime_type = models.ForeignKey('OneTimeJob', related_name='job_extras_set', null=True, blank=True,
                                     on_delete=models.PROTECT)
    extra_type = models.ForeignKey('JobExtraType', related_name='job_types_set', null=False, blank=False,
                                   on_delete=models.PROTECT)
    per_member = models.BooleanField(
        _('jeder kann Extra auswählen'), default=False)

    def empty(self, assignment_set):
        ids = [assignment.id for assignment in assignment_set]
        return self.assignments.filter(id__in=ids).count() == 0

    @property
    def type(self):
        if self.recuring_type is not None:
            return self.recuring_type
        return self.onetime_type

    def __str__(self):
        target = self.recuring_type or self.onetime_type
        return '%s:%s' % (self.extra_type, target)

    class Meta:
        verbose_name = _('JobExtra')
        verbose_name_plural = _('JobExtras')


class AbstractJobType(JuntagricoBaseModel):
    '''
    Abstract type of job.
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True,
                            help_text='Eindeutiger Name des Einsatzes')
    displayed_name = models.CharField(_('Angezeigter Name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('Beschreibung'), max_length=1000, default='')
    activityarea = models.ForeignKey(ActivityArea, on_delete=models.PROTECT, verbose_name=_('Tätigkeitsbereich'))
    default_duration = models.FloatField(_('Dauer in Stunden'),
                                         help_text='Standard-Dauer für diese Jobart', validators=[MinValueValidator(0)])
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name=_('Ort'))

    def __str__(self):
        return '%s - %s' % (self.activityarea, self.get_name)

    @property
    def get_name(self):
        if self.displayed_name is not None and self.displayed_name != '':
            return self.displayed_name
        return self.name

    class Meta:
        abstract = True


class JobType(AbstractJobType):
    '''
    Recuring type of job. do only add fields here you do not need in a onetime job
    '''
    visible = models.BooleanField(_('Sichtbar'), default=True)

    contact_set = GenericRelation(Contact)

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        return self.activityarea.contacts

    def get_emails(self):
        return get_emails(self.contact_set, self.activityarea.get_emails)

    class Meta:
        verbose_name = _('Jobart')
        verbose_name_plural = _('Jobarten')


@absolute_url(name='job')
class Job(JuntagricoBasePoly):
    slots = models.PositiveIntegerField(_('Plätze'), default=0)
    infinite_slots = models.BooleanField(_('Unendlich Plätze'), default=False)
    time = models.DateTimeField(_('Zeitpunkt'))
    multiplier = models.PositiveIntegerField(
        _('{0} vielfaches').format(Config.vocabulary('assignment')), default=1)
    pinned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(
        _('Reminder verschickt'), default=False)
    canceled = models.BooleanField(_('abgesagt'), default=False)

    contact_set = GenericRelation(Contact)

    @property
    def type(self):
        raise NotImplementedError

    def __str__(self):
        return _('Job {0}').format(self.id)

    def weekday_name(self):
        day = self.time.isoweekday()
        return weekday_short(day, 2)

    def time_stamp(self):
        return int(time.mktime(self.time.timetuple()) * 1000)

    @property
    @admin.display(description=_('Freie Plätze'))
    def free_slots(self):
        if self.infinite_slots:
            return -1
        if not (self.slots is None):
            return self.slots - self.occupied_slots
        return 0

    @property
    def occupied_slots(self):
        return self.assignment_set.count()

    @property
    def duration(self):
        return self.type.default_duration

    def end_time(self):
        return self.time + timezone.timedelta(hours=self.duration)

    def start_time(self):
        return self.time

    def status_percentage(self):
        assignments = AssignmentDao.assignments_for_job(self.id)
        if self.slots < 1:
            return 100
        return assignments.count() * 100 / self.slots

    def is_core(self):
        return self.type.activityarea.core

    @property
    def get_css_classes(self):
        result = 'area-' + str(self.type.activityarea.pk)
        if self.canceled:
            result += ' canceled'
        return result

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

    @property
    def participants(self):
        return [a.member for a in self.assignment_set.all().prefetch_related('member') if a.member]

    @property
    def participant_names(self):
        return ", ".join([str(m) for m in self.participants])

    @property
    def participant_emails(self):
        return [m.email for m in self.participants]

    def clean(self):
        check_job_consistency(self)

    def can_modify(self, request):
        job_is_in_past = self.end_time() < timezone.now()
        job_is_running = self.start_time() < timezone.now()
        job_canceled = self.canceled
        job_read_only = job_canceled or job_is_running or job_is_in_past
        return not job_read_only or (
            request.user.is_superuser or request.user.has_perm('juntagrico.can_edit_past_jobs'))

    class Meta:
        verbose_name = _('AbstractJob')
        verbose_name_plural = _('AbstractJobs')
        permissions = (('can_edit_past_jobs', _('kann vergangene Jobs editieren')),)


class RecuringJob(Job):
    type = models.ForeignKey(JobType, on_delete=models.PROTECT, verbose_name=_('Jobart'))
    additional_description = models.TextField(_('Zusätzliche Beschreibung'), max_length=1000, blank=True, default='')
    duration_override = models.FloatField(
        _('Dauer in Stunden (Überschreibend)'), null=True, blank=True, default=None, validators=[MinValueValidator(0)],
        help_text=_('Wenn nicht angegeben, wird die Standard-Dauer von der Jobart übernommen.')
    )

    @property
    def duration(self):
        return self.duration_override if self.duration_override else super().duration

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        return self.type.contacts

    def get_emails(self):
        return get_emails(self.contact_set, self.type.get_emails)

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

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        return self.activityarea.contacts

    def get_emails(self):
        return get_emails(self.contact_set, self.activityarea.get_emails)

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        Job.pre_save(sender, instance)

    class Meta:
        verbose_name = _('EinzelJob')
        verbose_name_plural = _('EinzelJobs')


class Assignment(JuntagricoBaseModel):
    '''
    Single assignment (work unit).
    '''
    job = models.ForeignKey(Job, on_delete=models.PROTECT)
    member = models.ForeignKey('Member', on_delete=models.PROTECT, verbose_name=Config.vocabulary('member'))
    core_cache = models.BooleanField(_('Kernbereich'), default=False)
    job_extras = models.ManyToManyField(JobExtra, related_name='assignments', blank=True, verbose_name=_('Job Extras'))
    amount = models.FloatField(_('Wert'))

    def __str__(self):
        return '%s #%s' % (Config.vocabulary('assignment'), self.id)

    @admin.display(ordering='job__time')
    def time(self):
        return self.job.time

    def is_core(self):
        return self.job.type.activityarea.core

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        instance.core_cache = instance.is_core()

    def can_modify(self, request):
        return self.job.can_modify(request)

    class Meta:
        verbose_name = Config.vocabulary('assignment')
        verbose_name_plural = Config.vocabulary('assignment_pl')
