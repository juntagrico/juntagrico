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
    ).send_to(area.get_email())


def member_left_activityarea(area, member):
    EmailSender.get_sender(
        organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
        _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
          'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
            member.first_name, member.last_name, area.name
        ),
    ).send_to(area.get_email())


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
    if not hasattr(member, 'comment'):
        member.comment = ''
    EmailSender.get_sender(
        organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
        get_email_content('a_member_created', base_dict(locals())),
        bcc=kwargs['emails']
    ).send()


@requires_someone_with_perm('notified_on_member_cancellation')
def member_canceled(member, end_date, message, **kwargs):
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
