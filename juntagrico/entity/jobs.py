from functools import cached_property
from itertools import zip_longest

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, Max, F
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from polymorphic.managers import PolymorphicManager

from juntagrico.config import Config
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity import JuntagricoBaseModel, JuntagricoBasePoly, absolute_url
from juntagrico.entity.contact import get_emails, MemberContact, Contact
from juntagrico.entity.location import Location
from juntagrico.lifecycle.job import check_job_consistency
from juntagrico.queryset.job import JobQueryset, AssignmentQuerySet


@absolute_url(name='area')
class ActivityArea(JuntagricoBaseModel):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Beschreibung'), default='')
    core = models.BooleanField(_('Kernbereich'), default=False)
    hidden = models.BooleanField(
        _('versteckt'), default=False,
        help_text=_('Nicht auf der "Tätigkeitsbereiche"-Seite anzeigen. Einsätze bleiben sichtbar.'))
    coordinators = models.ManyToManyField('Member', verbose_name=_('Koordinatoren'), through='AreaCoordinator',
                                          related_name='coordinated_areas')
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
        # last resort: show area admins as contact
        return [MemberContact(member=m) for m in self.coordinators.all()]

    def _get_email_fallback(self, get_member=False, exclude=None):
        emails = []
        for coordinator in self.coordinators.all():
            if exclude is None or coordinator.email not in exclude:
                if get_member:
                    emails.append((coordinator.email, coordinator))
                else:
                    emails.append(coordinator.email)
        return emails

    def get_emails(self, get_member=False, exclude=None):
        """
        :param get_member: If true returns a member (or None) in addition to the email address
        :param exclude: List of email addresses to exclude
        :return: list of email addresses of area coordinator(s) or,
                 if `get_member` is true, a list of tuples with email and member object
        """
        return get_emails(self.contact_set, self._get_email_fallback, get_member, exclude)

    class Meta:
        verbose_name = _('Tätigkeitsbereich')
        verbose_name_plural = _('Tätigkeitsbereiche')
        ordering = ['sort_order']


class AreaCoordinator(JuntagricoBaseModel):
    area = models.ForeignKey(ActivityArea, related_name='coordinator_access', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', related_name='area_access', on_delete=models.PROTECT)
    can_modify_area = models.BooleanField(_('Kann Beschreibung ändern'), default=True)
    can_view_member = models.BooleanField(_('Kann {0} sehen').format(Config.vocabulary('member_pl')), default=True)
    can_contact_member = models.BooleanField(_('Kann {0} kontaktieren').format(Config.vocabulary('member_pl')), default=True)
    can_remove_member = models.BooleanField(_('Kann {0} entfernen').format(Config.vocabulary('member_pl')), default=True)
    can_modify_jobs = models.BooleanField(_('Kann Jobs verwalten'), default=True)
    can_modify_assignments = models.BooleanField(_('Kann Einsatzanmeldungen verwalten'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    class Meta:
        verbose_name = _('Koordinator')
        verbose_name_plural = _('Koordinatoren')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['area', 'member'], name='unique_area_member'),
        ]


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

    def display(self):
        per_member = ' (M)' if self.per_member else ''
        return str(self.extra_type) + per_member

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
    description = models.TextField(_('Beschreibung'), default='')
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

    @classmethod
    def make_unique_name(cls, name, start=2):
        def candidates():
            time_str = date_format(timezone.now(), "SHORT_DATETIME_FORMAT")
            yield name
            yield name + f' ({time_str})'
            index = start
            while True:
                yield name + f' ({time_str}/{index})'
                index += 1
        for name in candidates():
            if not cls.objects.filter(name=name).exists():
                return name
        return name + ' 42'

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

    def get_emails(self, get_member=False, exclude=None):
        """
        :param get_member: If true returns a member (or None) in addition to the email address
        :param exclude: List of email addresses to exclude
        :return: list of email addresses of job type coordinator(s) or,
                 if `get_member` is true, a list of tuples with email and member object
        """
        return get_emails(self.contact_set, self.activityarea.get_emails, get_member, exclude)

    class Meta:
        verbose_name = _('Jobart')
        verbose_name_plural = _('Jobarten')


@absolute_url(name='job')
class Job(JuntagricoBasePoly):
    slots = models.PositiveIntegerField(_('Plätze'), default=0)
    infinite_slots = models.BooleanField(_('Unendlich Plätze'), default=False)
    time = models.DateTimeField(_('Zeitpunkt'))
    multiplier = models.FloatField(
        _('{0} vielfaches').format(Config.vocabulary('assignment')), default=1.0,
        validators=[MinValueValidator(0)])
    pinned = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(
        _('Reminder verschickt'), default=False)
    canceled = models.BooleanField(_('abgesagt'), default=False)

    members = models.ManyToManyField('Member', through='Assignment', related_name='jobs')

    contact_set = GenericRelation(Contact)

    objects = PolymorphicManager.from_queryset(JobQueryset)()

    @property
    def type(self):
        raise NotImplementedError

    def __str__(self):
        return _('Job {0}').format(self.id)

    def get_label(self):
        return f'{self.type.get_name} ({date_format(self.time, "SHORT_DATETIME_FORMAT")})'

    @property
    @admin.display(description=_('Freie Plätze'))
    def free_slots(self):
        if self.infinite_slots:
            return -1
        if self.slots is not None:
            return self.slots - self.occupied_slots
        return 0

    @admin.display(description=_('Plätze'), ordering='slots')
    def slots_display(self):
        if self.infinite_slots:
            return mark_safe('&infin;')
        return self.slots

    @admin.display(description=_('Freie Plätze'))
    def free_slots_display(self):
        if self.infinite_slots:
            return mark_safe('&infin;')
        return self.free_slots

    @property
    def occupied_slots(self):
        return self.assignment_set.count()

    @property
    def duration(self):
        return self.type.default_duration

    def end_time(self):
        return self.time + timezone.timedelta(hours=self.duration)

    def has_ended(self, time=None):
        time = time or timezone.now()
        return self.end_time() < time

    def start_time(self):
        return self.time

    def has_started(self, time=None):
        time = time or timezone.now()
        return self.start_time() < time

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
        return self.members.all()

    @property
    def unique_participants(self):
        return self.participants.annotate(slots=Count('id')).distinct()

    @cached_property
    def all_participant_extras(self):
        extras = {}
        for assignment in self.assignment_set.all():
            if assignment.member not in extras:
                extras[assignment.member] = []
            for extra in assignment.job_extras.all():
                extras[assignment.member].append(extra)
        return extras

    @property
    def participant_names(self):
        return ", ".join([str(m) for m in self.participants])

    @property
    def participant_emails(self):
        return set(m.email for m in self.participants)

    def get_emails(self, get_member=False, exclude=None):
        """
        :param get_member: If true returns a member (or None) in addition to the email address
        :param exclude: List of email addresses to exclude
        :return: list of email addresses of job coordinator(s) or,
                 if `get_member` is true, a list of tuples with email and member object
        """
        raise NotImplementedError

    def contacts(self):
        """
        :return: list job coordinator(s)
        """
        raise NotImplementedError

    def clean(self):
        check_job_consistency(self)

    def check_if(self, user):
        return CheckJobCapabilities(user, self)

    class Meta:
        verbose_name = _('AbstractJob')
        verbose_name_plural = _('AbstractJobs')
        permissions = (('can_edit_past_jobs', _('kann vergangene Jobs editieren')),)


class CheckJobCapabilities:
    def __init__(self, user, job):
        self.user = user
        self.job = job
        self.access = self.job.type.activityarea.coordinator_access.filter(member__user=self.user).first()

    @cached_property
    def job_model_name(self):
        return self.job.get_real_instance_class().__name__.lower()

    @property
    def is_coordinator(self):
        return self.access and self.access.can_modify_jobs

    @property
    def is_assignment_coordinator(self):
        return self.access and self.access.can_modify_assignments

    def can_modify_assignments(self):
        return self.user.has_perm('juntagrico.change_assignment') or self.is_assignment_coordinator

    def can_contact_member(self):
        return self.user.has_perm('juntagrico.can_send_mails') or self.access and self.access.can_contact_member

    def get_edit_url(self):
        if self.user.has_perm(f'juntagrico.change_{self.job_model_name}') or self.is_coordinator:
            return reverse(f'admin:juntagrico_{self.job_model_name}_change', args=(self.job.id,))
        return ''

    def can_convert(self):
        return self.user.has_perm(f'juntagrico.change_{self.job_model_name}') or self.is_coordinator

    def can_modify(self):
        job_read_only = self.job.canceled or self.job.has_started()
        return not job_read_only or self.user.has_perm('juntagrico.can_edit_past_jobs')

    def can_copy(self):
        is_recurring = isinstance(self.job.get_real_instance(), RecuringJob)
        return is_recurring and (self.user.has_perm('juntagrico.add_recuringjob') or self.is_coordinator)

    def can_cancel(self):
        can_change = self.user.has_perm(f'juntagrico.change_{self.job_model_name}') or self.is_coordinator
        return not (self.job.canceled or self.job.has_started()) and can_change


def get_job_admin_url(request, job, has_perm=False):
    model = job.get_real_instance_class().__name__.lower()
    if has_perm or request.user.has_perm(f'juntagrico.change_{model}'):
        return reverse(f'admin:juntagrico_{model}_change', args=(job.id,))
    return ''


class RecuringJob(Job):
    type = models.ForeignKey(JobType, on_delete=models.PROTECT, verbose_name=_('Jobart'))
    additional_description = models.TextField(_('Zusätzliche Beschreibung'), blank=True, default='')
    duration_override = models.FloatField(
        _('Dauer in Stunden (Überschreibend)'), null=True, blank=True, default=None, validators=[MinValueValidator(0)],
        help_text=_('Wenn nicht angegeben, wird die Standard-Dauer von der Jobart übernommen.')
    )

    @property
    @admin.display(description=_('Dauer'))
    def duration(self):
        return self.duration_override if self.duration_override else super().duration

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        return self.type.contacts

    def get_emails(self, get_member=False, exclude=None):
        return get_emails(self.contact_set, self.type.get_emails, get_member, exclude)

    def convert(self):
        job_type = self.type
        additional_description = '\n' + self.additional_description if self.additional_description else ''
        one_time_job = OneTimeJob.objects.create(
            # from job type (mostly)
            name=OneTimeJob.make_unique_name(job_type.get_name),
            displayed_name=job_type.get_name,
            description=job_type.description + additional_description,
            activityarea=job_type.activityarea,
            default_duration=self.duration,
            location=job_type.location,
            # from recurring job
            slots=self.slots,
            infinite_slots=self.infinite_slots,
            time=self.time,
            multiplier=self.multiplier,
            pinned=self.pinned,
            reminder_sent=self.reminder_sent,
            canceled=self.canceled,
        )
        one_time_job.assignment_set.set(self.assignment_set.all())
        contacts = self.contact_set if self.contact_set.count() else job_type.contact_set
        for contact in contacts.all():
            one_time_job.contact_set.add(contact.copy(), bulk=False)
        for job_extra in job_type.job_extras_set.all():
            JobExtra.objects.create(
                onetime_type=one_time_job,
                extra_type=job_extra.extra_type,
                per_member=job_extra.per_member,
            )
        # workaround: deletion of polymorphic relations is unreliable.
        # this may be fixed soon https://github.com/jazzband/django-polymorphic/pull/746
        for contact in self.contact_set.all():
            contact.delete()
        self.delete()
        # TODO: add option to delete type if it isn't used anymore.
        return one_time_job

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

    def get_emails(self, get_member=False, exclude=None):
        return get_emails(self.contact_set, self.activityarea.get_emails, get_member, exclude)

    def convert(self, to_job_type=None):
        is_new_type = to_job_type is None
        if is_new_type:
            # create new job type
            to_job_type = JobType.objects.create(
                name=JobType.make_unique_name(self.get_name),
                displayed_name=self.get_name,
                description=self.description,
                activityarea=self.activityarea,
                default_duration=self.default_duration,
                location=self.location,
            )
            for contact in self.contact_set.all():
                to_job_type.contact_set.add(contact, bulk=False)
            for job_extra in self.job_extras_set.all():
                job_extra.onetime_type = None
                job_extra.recuring_type = to_job_type
                job_extra.save()
        # create recurring job
        recurring_job = RecuringJob.objects.create(
            type=to_job_type,
            slots=self.slots,
            infinite_slots=self.infinite_slots,
            time=self.time,
            multiplier=self.multiplier,
            pinned=self.pinned,
            reminder_sent=self.reminder_sent,
            canceled=self.canceled,
        )
        recurring_job.assignment_set.set(self.assignment_set.all())
        if not is_new_type:
            # make new recurring job as close as possible to previous one time job
            if to_job_type.default_duration != self.default_duration:
                recurring_job.duration_override = self.default_duration
            # TODO: keep description somehow?
            recurring_job.save()
            # apply contact(s) of one time job if it doesn't match the existing types contact(s)
            for type_contact, job_contact in zip_longest(to_job_type.contacts, self.contacts):
                if type_contact is None or job_contact is None or type_contact.to_html() != job_contact.to_html():
                    for contact in self.contacts:
                        recurring_job.contact_set.add(contact.copy(), bulk=False)
                    break
        self.job_extras_set.all().delete()  # delete protected related items first
        # workaround: deletion of polymorphic relations is unreliable.
        # this may be fixed soon https://github.com/jazzband/django-polymorphic/pull/746
        for contact in self.contact_set.all():
            contact.delete()
        self.delete()
        return recurring_job

    def similar_job_types(self, limit):
        return JobType.objects.filter(
            activityarea=self.activityarea,
            location=self.location,
        ).annotate(last_used=Max('recuringjob__time')).order_by(F('last_used').desc(nulls_last=True))[:limit]

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

    objects = AssignmentQuerySet.as_manager()

    def __str__(self):
        return '%s #%s' % (Config.vocabulary('assignment'), self.id)

    @admin.display(ordering='job__time')
    def time(self):
        return self.job.time

    def is_core(self):
        return self.job.type.activityarea.core

    @classmethod
    def pre_save(cls, sender, instance, **kwargs):
        if not kwargs.get('raw', False):
            instance.core_cache = instance.is_core()

    def can_modify(self, request):
        return self.job.get_real_instance().check_if(request.user).can_modify()

    class Meta:
        verbose_name = Config.vocabulary('assignment')
        verbose_name_plural = Config.vocabulary('assignment_pl')
