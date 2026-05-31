import datetime

from gettext import gettext as _

from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.core import management
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.loader import get_template
from django.test import override_settings

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import RecuringJob, ActivityArea
from juntagrico.entity.member import Member
from juntagrico.entity.membership import Membership
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import membernotification, adminnotification
from juntagrico.mailer.adminnotification import member_joined_activityarea, member_left_activityarea


class Command(BaseCommand):
    help = "Prints the text of all notification emails using real data from the database, but without sending any emails."

    def add_arguments(self, parser):
        parser.add_argument('selected', nargs='*', type=str,
                            default='signup subscription share password job depot member membership activityarea')
        parser.add_argument('--language', '-l', type=str, default=None)

    # entry point used by manage.py
    @transaction.atomic(durable=True)
    @override_settings(EMAIL_BACKEND='juntagrico.backends.email.MailTextBackend')
    def handle(self, selected, language, *args, **options):
        # generate temporary test data to ensure that required objects are available
        management.call_command('generate_testdata')
        subscription = Subscription.objects.filter(parts__isnull=False).first()
        canceled_subscription = Subscription.objects.filter(end_date__isnull=False).first()
        future_parts = subscription.parts.all()
        canceled_part = subscription.parts.first()
        if Config.enable_shares():
            shares = list(Share.objects.all()[:2])
        job = RecuringJob.objects.filter(members__isnull=False).order_by('time')[0]
        member, co_member = Member.objects.filter(MemberDao.has_future_subscription())[:2]
        member_wo_subs = Member.objects.filter(subscriptionmembership__isnull=True)[0]
        depot, new_depot = Depot.objects.all()[:2]
        area = ActivityArea.objects.first()
        membership, created = Membership.objects.get_or_create(account=member)
        # ensure there is a recipient for these admin notifications
        member.user.user_permissions.add(
            *Permission.objects.filter(
                content_type__app_label='juntagrico',
                codename__in=[
                    'notified_on_subscription_creation',
                    'notified_on_subscription_cancellation',
                    'notified_on_subscriptionpart_creation',
                    'notified_on_subscriptionpart_cancellation',
                    'notified_on_share_creation',
                    'notified_on_share_cancellation',
                    'notified_on_member_creation',
                    'notified_on_member_cancellation',
                    'notified_on_depot_change',
                    'notified_on_membership_creation',
                    'notified_on_membership_cancellation',
                ]
            )
        )
        separator = '\n' + '-' * 72 + '\n'

        with override_settings(EMAIL_LANGUAGE=language):
            if 'signup' in selected:
                print('*** welcome  mit abo***')
                membernotification.welcome(member, 'password')

                print('*** welcome  ohne abo***')
                membernotification.welcome(member_wo_subs, 'password')

                print('*** co_welcome ***')
                membernotification.welcome_co_member(co_member, 'password', 1)

                print('*** co_added ***')
                membernotification.welcome_co_member(co_member, 'password', 2, False)

                print('*** confirm ***')
                membernotification.email_confirmation(member)

            if 'subscription' in selected:
                print('*** n_sub ***')
                adminnotification.subscription_created(subscription, _('Kommentar'))

                print('*** s_canceled ***')
                adminnotification.subscription_canceled(canceled_subscription, _('Nachricht'))

                print('*** mails/admin/subpart_created.txt (a_subpart_created) ***')
                adminnotification.subparts_created(future_parts, subscription)

                print('*** mails/admin/subpart_canceled.txt (a_subpart_canceled) ***')
                adminnotification.subpart_canceled(canceled_part)

                print('*** mails/member/subscription/part/canceled.txt ***')
                membernotification.part_canceled_for_you(canceled_part)

                print('*** mails/member/subscription/trial/continue.txt ***')
                membernotification.trial_continued_for_you(canceled_part, canceled_part)

                print('*** mails/member/co_member_left_subscription.txt (m_left_subscription) ***')
                membernotification.co_member_left_subscription(member, co_member, _('[Nachricht des Mitglieds]'))

            if 'share' in selected and Config.enable_shares():
                print('*** s_created ***')
                membernotification.shares_created(member, shares)

                print('*** a_share_created ***')
                adminnotification.share_created(shares[0])

                print('*** a_share_canceled ***')
                adminnotification.share_canceled(shares[0])

            if 'password' in selected:
                print('*** password ***')
                email = get_template(Config.emails('password')).render({
                    'email': 'email@email.org',
                    'password': 'password',
                    'protocol': 'https',
                    'domain': Site.objects.get_current().domain,
                    'uid': 'uid',
                    'token': 'token'
                })
                print(email, end=separator)

            if 'job' in selected:
                print('*** j_reminder ***')
                membernotification.job_reminder(job)

                print('*** j_canceled ***')
                membernotification.job_canceled(job)

                print('*** j_changed ***')
                membernotification.job_time_changed(job)

                print('*** j_signup ***')
                membernotification.job_signup(member, job, count=1)

                print('*** member/job/subscription_changed ***')
                membernotification.job_subscription_changed(member, job, count=1)

                print('*** member/job/unsubscribed ***')
                membernotification.job_unsubscribed(member, job, count=1)

                print('*** admin/job/signup ***')
                with override_settings(FIRST_JOB_INFO=[], ENABLE_NOTIFICATIONS=['job_subscribed']):
                    adminnotification.member_subscribed_to_job(job, member=member, count=1)

                print('*** admin/job/first_signup ***')
                with override_settings(FIRST_JOB_INFO=['overall']):
                    adminnotification.member_subscribed_to_job(job, member=member, count=1)

                print('*** admin/job/first_signup_in_area ***')
                with override_settings(FIRST_JOB_INFO=['per_area']):
                    adminnotification.member_subscribed_to_job(job, member=member, count=1)

                print('*** admin/job/first_signup_in_type ***')
                with override_settings(FIRST_JOB_INFO=['per_type']):
                    adminnotification.member_subscribed_to_job(job, member=member, count=1)

                print('*** admin/job/subscription_changed ***')
                adminnotification.member_changed_job_subscription(
                    job, member=member, count=1, initial_count=2, message=_('[Nachricht des Mitglieds]')
                )

                print('*** admin/job/unsubscribed ***')
                adminnotification.member_unsubscribed_from_job(
                    job, member=member, initial_count=1, message=_('[Nachricht des Mitglieds]')
                )

                assignment_context = dict(
                    job=job,
                    instance=member,
                    member=member,
                    editor=co_member,
                    initial_count=2,
                    count=1,
                    message='[Nachricht an Mitglied]'
                )
                print('*** member/assignment/changed ***')
                membernotification.assignment_changed(member, **assignment_context)

                print('*** member/assignment/removed ***')
                membernotification.assignment_removed(member, **assignment_context)

                print('*** admin/assignment/changed ***')
                adminnotification.assignment_changed(**assignment_context)

                print('*** admin/assignment/removed ***')
                adminnotification.assignment_removed(**assignment_context)

            if 'depot' in selected:
                print('*** d_changed ***')
                membernotification.depot_changed(subscription)

                print('*** juntagrico/mails/admin/depot_changed.txt ***')
                depot_changed_context = {
                    'subscription': subscription,
                    'member': member,
                    'old_depot': depot,
                    'new_depot': new_depot,
                }
                adminnotification.member_changed_depot(**depot_changed_context)

                print('*** juntagrico/mails/admin/depot_changed.txt immediate ***')
                adminnotification.member_changed_depot(**depot_changed_context, immediate=True)

                print('*** a_depot_list_generated ***')
                adminnotification.depot_list_generated()

            if 'activityarea' in selected:
                print('*** member_joined_activityarea ***')
                member_joined_activityarea(area, member)

                print('*** member_left_activityarea ***')
                member_left_activityarea(area, member)

            if 'member' in selected:
                print('*** a_member_created ***')
                adminnotification.member_created(member)

                print('*** m_canceled ***')
                member.end_date = datetime.date.today()
                adminnotification.member_canceled(member, _('[Nachricht des Mitglieds]'))

            if 'membership' in selected:
                print('*** juntagrico/mails/admin/membership/created.txt ***')
                adminnotification.membership_created(membership, _('[Nachricht des Mitglieds]'))

                print('*** juntagrico/mails/admin/membership/canceled.txt ***')
                adminnotification.membership_canceled(member, _('[Nachricht des Mitglieds]'))

                print('*** juntagrico/mails/member/membership/activated.txt ***')
                membernotification.membership_activated(membership)

                print('*** juntagrico/mails/member/membership/deactivated.txt ***')
                membernotification.membership_deactivated(membership)

        transaction.set_rollback(True)  # force rollback
