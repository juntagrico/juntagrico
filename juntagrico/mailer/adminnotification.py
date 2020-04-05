from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import get_email_content, base_dict, get_emails_by_permission, organisation_subject
from juntagrico.mailer.emailsender import prepare_email, send_to, send


"""
Admin notification emails
"""

def member_joined_activityarea(area, member):
    email = prepare_email(
        organisation_subject(_('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name)),
        _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
            member.first_name, member.last_name, area.name
        )
    )
    send_to(email, area.get_email())


def member_left_activityarea(area, member):
    email = prepare_email(
        organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
        _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
          'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
            member.first_name, member.last_name, area.name
        ),
    )
    send_to(email, area.get_email())


def subscription_created(subscription):
    email= prepare_email(
        organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('subscription'))),
        get_email_content('n_sub', base_dict(locals())),
        bcc=get_emails_by_permission('notified_on_subscription_creation')
    )
    send(email)


def subscription_canceled(subscription, message):
    email = prepare_email(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('subscription'))),
        get_email_content('s_canceled', base_dict(locals())),
        bcc=get_emails_by_permission('notified_on_subscription_cancellation')
    )
    send(email)


def share_created(share):
    email = prepare_email(
        organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('share'))),
        get_email_content('a_share_created', base_dict(locals())),
        bcc=get_emails_by_permission('notified_on_share_creation')
    )
    send(email)


def member_created(member):
    email = prepare_email(
        organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
        get_email_content('a_member_created', base_dict(locals())),
        bcc=get_emails_by_permission('notified_on_member_creation')
    )
    send(email)


def member_canceled(member, end_date, message):
    email = prepare_email(
        organisation_subject(_('{} gekündigt').format(Config.vocabulary('member_type'))),
        get_email_content('m_canceled', base_dict(locals())),
        bcc=get_emails_by_permission('notified_on_member_cancellation')
    )
    send(email)
