from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import get_email_content, base_dict, organisation_subject
from juntagrico.mailer.emailsender import prepare_email, send_to, send, start_thread, attach_ics, \
    continue_thread
from juntagrico.util.ical import generate_ical_for_job
from juntagrico.util.organisation_name import enriched_organisation


"""
Member notification emails
"""

def welcome(member, password):
    email = prepare_email(
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('welcome', base_dict(locals())),
    )
    send_to(email, member.email)


def welcome_co_member(co_member, password, new_shares, new=True):
    # sends either welcome mail or just information mail to new/added co-member
    email = prepare_email(
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('co_welcome' if new else 'co_added', base_dict(locals())),
    )
    send_to(email, co_member.email)


def shares_created(member, shares):
    email = prepare_email(
        organisation_subject(_('Dein neuer Anteilschein')),
        get_email_content('s_created', base_dict(locals())),
    )
    send_to(email, member.email)


def email_confirmation(member):
    d = {'hash': member.get_hash()}
    email= prepare_email(
        organisation_subject(_('E-Mail-Adresse bestätigen')),
        get_email_content('confirm', base_dict(d)),
    )
    send_to(email, member.email)


def reset_password(email_adr, password):
    email = prepare_email(
        organisation_subject(_('Dein neues Passwort')),
        get_email_content('password', base_dict(locals())),
    )
    send_to(email, email_adr)


def depot_changed(emails, depot):
    email = prepare_email(
        organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
        get_email_content('d_changed', base_dict(locals())),
        bcc=emails
    )
    send(email)


def co_member_left_subscription(primary_member, co_member, message):
    email = prepare_email(
        organisation_subject(_('Austritt aus {}').format(Config.vocabulary('subscription'))),
        get_email_content('m_left_subscription', base_dict(locals())),
        to=[primary_member.email]
    )
    send(email)


def job_signup(email_adr, job):
    email = prepare_email(
        organisation_subject(_('Für Einsatz angemeldet')),
        get_email_content('j_signup', base_dict(locals()))
    )
    start_thread(email, repr(job))
    attach_ics(email, generate_ical_for_job(job))
    send_to(email, email_adr)


def job_reminder(emails, job, participants):
    contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
    email = prepare_email(
        organisation_subject(_('Einsatz-Erinnerung')),
        get_email_content('j_reminder', base_dict(locals())),
        bcc=emails
    )
    attach_ics(email, generate_ical_for_job(job))
    continue_thread(email, repr(job))
    send(email)


def job_time_changed(emails, job):
    email = prepare_email(
        organisation_subject(_('Einsatz-Zeit geändert')),
        get_email_content('j_changed', base_dict(locals())),
        bcc=emails
    )
    attach_ics(email, generate_ical_for_job(job))
    continue_thread(email, repr(job))
    send(email)


def job_canceled(emails, job):
    email = prepare_email(
        organisation_subject(_('Einsatz abgesagt')),
        get_email_content('j_canceled', base_dict(locals())),
        bcc=emails
    )
    continue_thread(email, repr(job))
    send(email)
