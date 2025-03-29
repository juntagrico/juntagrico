from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailSender, organisation_subject, get_email_content, base_dict, \
    requires_someone_with_perm

"""
Admin notification emails
"""


def member_joined_activityarea(area, member):
    EmailSender.get_sender(
        organisation_subject(_('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name)),
        _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
            member.first_name, member.last_name, area.name
        ),
    ).send_to(area.get_emails())


def member_left_activityarea(area, member):
    EmailSender.get_sender(
        organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
        _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
          'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
            member.first_name, member.last_name, area.name
        ),
    ).send_to(area.get_emails())


@requires_someone_with_perm('notified_on_subscription_creation')
def subscription_created(subscription, comment='', **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('subscription'))),
        get_email_content('n_sub', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_subscription_cancellation')
def subscription_canceled(subscription, message, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('subscription'))),
        get_email_content('s_canceled', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_subscriptionpart_creation')
def subparts_created(parts, subscription, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Neuer Bestandteil erstellt')),
        get_email_content('a_subpart_created', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_subscriptionpart_cancellation')
def subpart_canceled(part, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Bestandteil gekündigt')),
        get_email_content('a_subpart_canceled', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_share_creation')
def share_created(share, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('share'))),
        get_email_content('a_share_created', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_share_cancellation')
def share_canceled(share, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('share'))),
        get_email_content('a_share_canceled', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_member_creation')
def member_created(member, **kwargs):
    member.comment = member.signup_comment  # backwards compatibility
    EmailSender.get_sender(
        organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
        get_email_content('a_member_created', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_member_cancellation')
def member_canceled(member, message='', **kwargs):
    end_date = member.end_date
    EmailSender.get_sender(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('member_type'))),
        get_email_content('m_canceled', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('depot_list_notification')
def depot_list_generated(**kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Neue {}-Liste generiert').format(Config.vocabulary('depot'))),
        get_email_content('a_depot_list_generated', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_depot_change')
def member_changed_depot(**kwargs):
    EmailSender.get_sender(
        organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
        get_template('juntagrico/mails/admin/depot_changed.txt').render(base_dict(kwargs)),
        bcc=kwargs['emails']
    ).send()


def _template_member_in_job(job, subject, template_name, **kwargs):
    kwargs['job'] = job
    EmailSender.get_sender(
        organisation_subject(subject),
        get_template(f'juntagrico/mails/admin/job/{template_name}.txt').render(base_dict(kwargs)),
        to=job.get_emails(),
        reply_to=[kwargs['member'].email],
    ).send()


def member_subscribed_to_job(job, **kwargs):
    # TODO: Allow contacts to subscribe/unsubscribe from notifications
    if kwargs.get('message'):
        subject = _('Neue Anmeldung zum Einsatz mit Mitteilung')
    else:
        if not Config.notifications('job_subscribed'):
            return
        subject = _('Neue Anmeldung zum Einsatz')
    _template_member_in_job(job, subject, 'signup', **kwargs)


def member_changed_job_subscription(job, **kwargs):
    if Config.notifications('job_subscription_changed') or kwargs.get('message'):
        _template_member_in_job(job, _('Änderung der Einsatzanmeldung'), 'changed_subscription', **kwargs)


def member_unsubscribed_from_job(job, **kwargs):
    if Config.notifications('job_unsubscribed') or kwargs.get('message'):
        _template_member_in_job(job, _('Abmeldung vom Einsatz'), 'unsubscribed', **kwargs)


def _template_assignment_changed(job, subject, template_name, **kwargs):
    to = job.get_emails(exclude=kwargs['editor'].email)
    if to:
        kwargs['job'] = job
        EmailSender.get_sender(
            organisation_subject(subject),
            get_template(f'juntagrico/mails/admin/assignment/{template_name}.txt').render(base_dict(kwargs)),
            to=to,
            reply_to=[kwargs['editor'].email],
        ).send()


def assignment_changed(job, **kwargs):
    _template_assignment_changed(job, _('Änderung der Einsatzanmeldung'), 'changed', **kwargs)


def assignment_removed(job, **kwargs):
    _template_assignment_changed(job, _('Einsatzanmeldung entfernt'), 'removed', **kwargs)
