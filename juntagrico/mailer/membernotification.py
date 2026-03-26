from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from juntagrico.config import Config
from juntagrico.mailer import EmailBuilder, EmailSender, organisation_subject, get_template, base_dict
from juntagrico.util.organisation_name import enriched_organisation

"""
Member notification emails
"""


def welcome(member, password):
    EmailBuilder(
        member,
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        'welcome',
        {'password': password},
        'for_members',
    ).send()


def welcome_co_member(co_member, password, new_shares, new=True):
    # sends either welcome mail or just information mail to new/added co-member
    EmailBuilder(
        co_member,
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        'co_welcome' if new else 'co_added',
        {
            'password': password,
            'new_shares': new_shares,
            'sub': co_member.subscription_future or co_member.subscription_current,
        },
        'for_members',
    ).send()


def shares_created(member, shares):
    EmailBuilder(
        member,
        _('Dein neuer {share}').format(share=Config.vocabulary('share')),
        's_created',
        {
            'shares': shares,
            'total': len(shares) * int(Config.share_price())
        },
        'for_shares',
    ).send()


def email_confirmation(member):
    EmailBuilder(
        member,
        _('E-Mail-Adresse bestätigen'),
        'confirm',
        from_email='technical',
    ).send()


def membership_activated(membership):
    if Config.notifications('membership_activated'):
        EmailSender.get_sender_for_contact(
            'for_members',
            organisation_subject(_('{} aktiviert').format(Config.vocabulary('membership'))),
            get_template('juntagrico/mails/member/membership/activated.txt').render(base_dict({
                'account': membership.account,
            })),
            to=[membership.account.email],
        ).send()


def membership_deactivated(membership):
    if Config.notifications('membership_deactivated'):
        EmailSender.get_sender_for_contact(
            'for_members',
            organisation_subject(_('{} deaktiviert').format(Config.vocabulary('membership'))),
            get_template('juntagrico/mails/member/membership/deactivated.txt').render(base_dict({
                'account': membership.account,
            })),
            to=[membership.account.email],
        ).send()


def depot_changed(subscription):
    EmailBuilder(
        subscription.current_members,
        capfirst(_('{depot} geändert')).format(depot=Config.vocabulary('depot')),
        'd_changed',
        {
            'subscription': subscription,
        },
        'for_subscriptions',
    ).send()


def co_member_left_subscription(primary_member, co_member, message):
    EmailBuilder(
        primary_member,
        _('Austritt aus {subscription}').format(subscription=Config.vocabulary('subscription')),
        'm_left_subscription',
        {
            'co_member': co_member,
            'message': message,
        },
        'for_subscriptions',
    ).send()


def part_canceled_for_you(part):
    member = part.subscription.primary_member
    if member is not None:
        EmailBuilder(
            member,
            _('Bestandteil gekündigt'),
            'juntagrico/mails/member/subscription/part/canceled.txt',
            {
                'part': part,
            },
            'for_subscriptions'
        ).send()


def trial_continued_for_you(trial_part, follow_up_part):
    member = trial_part.subscription.primary_member
    if member is not None:
        EmailBuilder(
            member,
            _('Fortsetzung nach Probe-{subscription}').format(subscription=Config.vocabulary('subscription')),
            'juntagrico/mails/member/subscription/trial/continue.txt',
            {
                'trial_part': trial_part,
                'follow_up_part': follow_up_part,
            },
            'for_subscriptions'
        ).send()


def job_signup(participant, job, count):
    EmailBuilder(
        participant,
        _('Für Einsatz angemeldet'),
        'j_signup',
        {
            'job': job,
            'count': count,
        },
    ).attach(job.to_email_attachment).start_thread(job).send()


def job_subscription_changed(participant, job, count):
    EmailBuilder(
        participant,
        _('Einsatzanmeldung geändert'),
        'juntagrico/mails/member/job/subscription_changed.txt',
        {
            'job': job,
            'count': count,
        },
    ).continue_thread(job).send()


def job_unsubscribed(participant, job, count):
    EmailBuilder(
        participant,
        _('Von Einsatz abgemeldet'),
        'juntagrico/mails/member/job/unsubscribed.txt',
        {
            'job': job,
            'count': count,
        },
    ).continue_thread(job).send()


def assignment_changed(participant, **kwargs):
    EmailBuilder(
        participant,
        _('Einsatz geändert'),
        'juntagrico/mails/member/assignment/changed.txt',
        kwargs,
        reply_to=[kwargs.get('editor').email]
    ).continue_thread(kwargs['job']).send()


def assignment_removed(participant, **kwargs):
    EmailBuilder(
        participant,
        _('Einsatz gelöscht'),
        'juntagrico/mails/member/assignment/removed.txt',
        kwargs,
        reply_to=[kwargs.get('editor').email]
    ).continue_thread(kwargs['job']).send()


def job_reminder(job):
    if recipients := job.members.distinct():
        EmailBuilder(
            recipients,
            _('Einsatz-Erinnerung'),
            'j_reminder',
            {
                'job': job,
            },
        ).attach(job.to_email_attachment).continue_thread(job).send()


def job_time_changed(job):
    if recipients := job.members.distinct():
        EmailBuilder(
            recipients,
            _('Einsatz-Zeit geändert'),
            'j_changed',
            {
                'job': job,
            },
        ).attach(job.to_email_attachment).continue_thread(job).send()


def job_canceled(job):
    if recipients := job.members.distinct():
        EmailBuilder(
            recipients,
            _('Einsatz abgesagt'),
            'j_canceled',
            {
                'job': job,
            },
        ).continue_thread(job).send()
