from django.template.loader import get_template
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from juntagrico.config import Config
from juntagrico.mailer import EmailBuilder, requires_someone_with_perm, EmailSender, organisation_subject, base_dict

"""
Admin notification emails
"""


def member_joined_activityarea(area, member):
    EmailBuilder(
        area.get_emails(get_member=True),
        _('Neue/r/s {member_type} im Tätigkeitsbereich {area}').format(
            member_type=Config.vocabulary('member_type'),
            area=area.name
        ),
        'admin',
        _('Soeben hat sich {member} in den Tätigkeitsbereich {area} eingetragen.').format(
            member=member,
            area=area.name
        ),
    ).send()


def member_left_activityarea(area, member):
    EmailBuilder(
        area.get_emails(get_member=True),
        capfirst(_('{member_type} verlässt Tätigkeitsbereich {area}').format(
            member_type=Config.vocabulary('member_type'),
            area=area.name
        )),
        'admin',
        _('Soeben hat sich {member} aus dem Tätigkeitsbereich {area} ausgetragen. '
          'Bitte lösche seine/ihre Kontaktdaten aus allen deinen privaten Adressbüchern.').format(
            member=member,
            area=area.name
        ),
    ).send()


def subscription_created(subscription, comment=''):
    EmailBuilder(
        'notified_on_subscription_creation',
        capfirst(_('Neue/r/s {subscription} erstellt').format(
            subscription=Config.vocabulary('subscription')
        )),
        'n_sub',
        {
            'subscription': subscription,
            'comment': comment,
        },
    ).send()


def subscription_canceled(subscription, message):
    EmailBuilder(
        'notified_on_subscription_cancellation',
        capfirst(_('{subscription} gekündigt').format(
            subscription=Config.vocabulary('subscription')
        )),
        's_canceled',
        {
            'subscription': subscription,
            'message': message,
        },
    ).send()


def subparts_created(parts, subscription):
    EmailBuilder(
        'notified_on_subscriptionpart_creation',
        _('Neuer Bestandteil erstellt'),
        'a_subpart_created',
        {
            'parts': parts,
            'subscription': subscription,
        },
    ).send()


def subpart_canceled(part):
    EmailBuilder(
        'notified_on_subscriptionpart_cancellation',
        _('Bestandteil gekündigt'),
        'a_subpart_canceled',
        {
            'part': part,
            'subscription': part.subscription
        },
    ).send()


def share_created(share):
    EmailBuilder(
        'notified_on_share_creation',
        _('Neue/r/s {share} erstellt').format(share=Config.vocabulary('share')),
        'a_share_created',
        {
            'share': share,
        },
    ).send()


def share_canceled(share):
    EmailBuilder(
        'notified_on_share_cancellation',
        capfirst(_('{share} gekündigt').format(share=Config.vocabulary('share'))),
        'a_share_canceled',
        {
            'share': share,
        },
    ).send()


def member_created(member):
    member.comment = member.signup_comment  # backwards compatibility
    EmailBuilder(
        'notified_on_member_creation',
        _('Neue/r/s {account}').format(account=Config.vocabulary('account')),
        'a_member_created',
        {
            'member': member,
        },
    ).send()


def member_canceled(member, message=''):
    EmailBuilder(
        'notified_on_member_cancellation',
        _('{account} gekündigt').format(account=Config.vocabulary('account')),
        'm_canceled',
        {
            'member': member,
            'message': message,
            'end_date': member.end_date,  # backwards compatibility
        },
    ).send()


@requires_someone_with_perm('notified_on_membership_creation')
def membership_created(membership, emails=None):
    EmailSender.get_sender(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('membership'))),
        get_template('juntagrico/mails/admin/membership/created.txt').render(base_dict({
            'account': membership.account
        })),
        bcc=emails or []
    ).send()


@requires_someone_with_perm('notified_on_membership_cancellation')
def membership_canceled(membership, message='', emails=None):
    EmailSender.get_sender(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('membership'))),
        get_template('juntagrico/mails/admin/membership/canceled.txt').render(base_dict({
            'account': membership.account,
            'message': message
        })),
        bcc=emails or []
    ).send()


def depot_list_generated():
    EmailBuilder(
        'depot_list_notification',
        _('Neue {depot}-Liste generiert').format(depot=Config.vocabulary('depot')),
        'a_depot_list_generated',
    ).send()


def member_changed_depot(**kwargs):
    EmailBuilder(
        'notified_on_depot_change',
        capfirst(_('{depot} geändert').format(depot=Config.vocabulary('depot'))),
        'juntagrico/mails/admin/depot_changed.txt',
        kwargs
    ).send()


def _template_member_in_job(job, subject, template_name, **kwargs):
    kwargs['job'] = job
    EmailBuilder(
        job.get_emails(get_member=True),
        subject,
        f'juntagrico/mails/admin/job/{template_name}.txt',
        kwargs,
        reply_to=[kwargs['member'].email],
    ).send()


def member_subscribed_to_job(job, **kwargs):
    # TODO: Allow contacts to subscribe/unsubscribe from notifications
    from juntagrico.entity.jobs import Job, RecuringJob
    member = kwargs['member']
    message = kwargs.get('message')
    if Config.notifications('first_job_subscribed') and job.is_first_for(member):
        # notification on first job signup of member
        template_name = 'first_signup'
        if message:
            subject = _('Erster Einsatz (mit Mitteilung)')
        else:
            subject = _('Erster Einsatz')
    elif Config.notifications('first_job_in_area_subscribed') and job.is_first_for(
            member, Job.objects.in_area(job.type.activityarea)
    ):
        # notification on first job signup of member in this area
        template_name = 'first_signup_in_area'
        if message:
            subject = _('Erster Einsatz im Tätigkeitsbereich "{}" (mit Mitteilung)').format(job.type.activityarea)
        else:
            subject = _('Erster Einsatz im Tätigkeitsbereich "{}"').format(job.type.activityarea)
    elif Config.notifications('first_job_in_type_subscribed') and isinstance(job, RecuringJob) and job.is_first_for(
            member, job.type.recuringjob_set.all()
    ):
        # notification on first job signup of member in this job type
        template_name = 'first_signup_in_type'
        if message:
            subject = _('Erster Einsatz in Job-Art "{}" (mit Mitteilung)').format(job.type.get_name)
        else:
            subject = _('Erster Einsatz in Job-Art "{}"').format(job.type.get_name)
    else:
        # normal signup notification
        template_name = 'signup'
        if message:
            subject = _('Neue Anmeldung zum Einsatz mit Mitteilung')
        else:
            if not Config.notifications('job_subscribed'):
                return
            subject = _('Neue Anmeldung zum Einsatz')
    _template_member_in_job(job, subject, template_name, **kwargs)


def member_changed_job_subscription(job, **kwargs):
    if Config.notifications('job_subscription_changed') or kwargs.get('message'):
        _template_member_in_job(job, _('Änderung der Einsatzanmeldung'), 'changed_subscription', **kwargs)


def member_unsubscribed_from_job(job, **kwargs):
    if Config.notifications('job_unsubscribed') or kwargs.get('message'):
        _template_member_in_job(job, _('Abmeldung vom Einsatz'), 'unsubscribed', **kwargs)


def _template_assignment_changed(job, subject, template_name, **kwargs):
    if recipients := job.get_emails(get_member=True, exclude=kwargs['editor'].email):
        kwargs['job'] = job
        kwargs['member'] = kwargs.get('instance')  # templates expect 'member', signal sends 'instance'
        EmailBuilder(
            recipients,
            subject,
            f'juntagrico/mails/admin/assignment/{template_name}.txt',
            kwargs,
            reply_to=[kwargs['member'].email],
        ).send()


def assignment_changed(job, **kwargs):
    _template_assignment_changed(job, _('Änderung der Einsatzanmeldung'), 'changed', **kwargs)


def assignment_removed(job, **kwargs):
    _template_assignment_changed(job, _('Einsatzanmeldung entfernt'), 'removed', **kwargs)
