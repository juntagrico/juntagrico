from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailSender, get_email_content, base_dict, organisation_subject
from juntagrico.util.ical import generate_ical_for_job
from juntagrico.util.organisation_name import enriched_organisation

"""
Member notification emails
"""


def welcome(member, password):
    EmailSender.get_sender_for_contact(
        'for_members',
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('welcome', base_dict(locals())),
    ).send_to(member.email)


def welcome_co_member(co_member, password, new_shares, new=True):
    # sends either welcome mail or just information mail to new/added co-member
    sub = co_member.subscription_future or co_member.subscription_current
    EmailSender.get_sender_for_contact(
        'for_members',
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('co_welcome' if new else 'co_added', base_dict(locals())),
    ).send_to(co_member.email)


def shares_created(member, shares):
    EmailSender.get_sender_for_contact(
        'for_shares',
        organisation_subject(_('Dein neuer Anteilschein')),
        get_email_content('s_created', base_dict(locals())),
    ).send_to(member.email)


def email_confirmation(member):
    d = {'hash': member.get_hash()}
    EmailSender.get_sender_for_contact(
        'technical',
        organisation_subject(_('E-Mail-Adresse bestätigen')),
        get_email_content('confirm', base_dict(d)),
    ).send_to(member.email)


def depot_changed(subscription, **kwargs):
    EmailSender.get_sender_for_contact(
        'for_subscriptions',
        organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
        get_email_content('d_changed', base_dict(locals())),
        to=[subscription.primary_member.email],
        cc=subscription.co_members().values_list('email', flat=True)
    ).send()


def co_member_left_subscription(primary_member, co_member, message):
    EmailSender.get_sender_for_contact(
        'for_subscriptions',
        organisation_subject(_('Austritt aus {}').format(Config.vocabulary('subscription'))),
        get_email_content('m_left_subscription', base_dict(locals())),
        to=[primary_member.email]
    ).send()


def job_signup(email, job, count):
    EmailSender.get_sender(
        organisation_subject(_('Für Einsatz angemeldet')),
        get_email_content('j_signup', base_dict(locals()))
    ).attach_ics(generate_ical_for_job(job)).start_thread(job).send_to(email)


def job_subscription_changed(email, job, count):
    EmailSender.get_sender(
        organisation_subject(_('Von Einsatz abgemeldet')),
        get_template('juntagrico/mails/member/job/subscription_changed.txt').render(base_dict(
            dict(job=job, count=count)
        ))
    ).continue_thread(job).send_to(email)


def job_unsubscribed(email, job, count):
    EmailSender.get_sender(
        organisation_subject(_('Von Einsatz abgemeldet')),
        get_template('juntagrico/mails/member/job/unsubscribed.txt').render(base_dict(
            dict(job=job, count=count)
        ))
    ).continue_thread(job).send_to(email)


def assignment_changed(email, job, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Einsatz geändert')),
        get_template('juntagrico/mails/member/assignment/changed.txt').render(base_dict({'job': job, **kwargs})),
        reply_to=[kwargs.get('editor').email]
    ).continue_thread(job).send_to(email)


def assignment_removed(email, job, **kwargs):
    EmailSender.get_sender(
        organisation_subject(_('Einsatz gelöscht')),
        get_template('juntagrico/mails/member/assignment/removed.txt').render(base_dict({'job': job, **kwargs})),
        reply_to=[kwargs.get('editor').email]
    ).continue_thread(job).send_to(email)


def job_reminder(emails, job):
    EmailSender.get_sender(
        organisation_subject(_('Einsatz-Erinnerung')),
        get_email_content('j_reminder', base_dict(locals())),
        bcc=emails
    ).attach_ics(generate_ical_for_job(job)).continue_thread(job).send()


def job_time_changed(emails, job):
    EmailSender.get_sender(
        organisation_subject(_('Einsatz-Zeit geändert')),
        get_email_content('j_changed', base_dict(locals())),
        bcc=emails
    ).attach_ics(generate_ical_for_job(job)).continue_thread(job).send()


def job_canceled(emails, job):
    EmailSender.get_sender(
        organisation_subject(_('Einsatz abgesagt')),
        get_email_content('j_canceled', base_dict(locals())),
        bcc=emails
    ).continue_thread(job).send()
