import datetime

from django.contrib.sites.models import Site
from django.core import management
from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.loader import get_template

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import get_email_content, base_dict


class Command(BaseCommand):
    help = "Prints the text of all notification emails using real data from the database, but without sending any emails."

    def add_arguments(self, parser):
        parser.add_argument('selected', nargs='*', type=str,
                            default='signup subscription share password job depot member')

    # entry point used by manage.py
    def handle(self, selected, *args, **options):
        with transaction.atomic(durable=True):
            # generate temporary test data to ensure that required objects are available
            management.call_command('generate_testdata')
            subscription = Subscription.objects.filter(parts__isnull=False).first()
            future_parts = subscription.parts.all()
            canceled_part = subscription.parts.first()
            if Config.enable_shares():
                shares = list(Share.objects.all()[:2])
            job = RecuringJob.objects.all()[0]
            member, co_member = Member.objects.filter(MemberDao.has_future_subscription())[:2]
            member_wo_subs = Member.objects.filter(subscriptionmembership__isnull=True)[0]
            depot, new_depot = Depot.objects.all()[:2]
            transaction.set_rollback(True)  # force rollback

        if 'signup' in selected:
            print('*** welcome  mit abo***')
            print(get_email_content('welcome', base_dict({
                'member': member,
                'password': 'password'
            })))
            print()

            print('*** welcome  ohne abo***')
            print(get_email_content('welcome', base_dict({
                'member': member_wo_subs,
                'password': 'password'
            })))
            print()

            print('*** co_welcome ***')
            print(get_email_content('co_welcome', base_dict({
                'co_member': co_member,
                'password': 'password',
                'sub': co_member.subscription_future or co_member.subscription_current
            })))
            print()

            print('*** co_added ***')
            print(get_email_content('co_added', base_dict({
                'co_member': co_member,
                'password': 'password',
                'new_shares': '9',
                'sub': co_member.subscription_future or co_member.subscription_current
            })))
            print()

            print('*** confirm ***')
            print(get_email_content('confirm', base_dict({'hash': 'hash'})))
            print()

        if 'subscription' in selected:
            print('*** n_sub ***')
            print(get_email_content('n_sub', base_dict({'subscription': subscription, 'comment': 'user comment'})))
            print()

            print('*** s_canceled ***')
            print(get_email_content('s_canceled', base_dict({
                'subscription': subscription,
                'message': 'Nachricht'
            })))
            print()

            print('*** mails/admin/subpart_created.txt (a_subpart_created) ***')
            print(get_email_content('a_subpart_created', base_dict({
                'subscription': subscription,
                'parts': future_parts,
            })), end='\n\n')

            print('*** mails/admin/subpart_canceled.txt (a_subpart_canceled) ***')
            print(get_email_content('a_subpart_canceled', base_dict({
                'part': canceled_part,
            })), end='\n\n')

            print('*** mails/member/co_member_left_subscription.txt (m_left_subscription) ***')
            print(get_email_content('m_left_subscription', base_dict({
                'primary_member': member,
                'co_member': co_member,
                'message': '[Nachricht des Mitglieds]',
            })), end='\n\n')

        if 'share' in selected and Config.enable_shares():
            print('*** s_created ***')
            print(get_email_content('s_created', base_dict({'shares': shares})))
            print()

            print('*** a_share_created ***')
            print(get_email_content('a_share_created', base_dict({
                'share': shares[0]
            })))
            print()

        if 'password' in selected:
            print('*** password ***')
            print(get_email_content('password', base_dict({
                'email': 'email@email.org',
                'password': 'password',
                'protocol': 'https',
                'domain': Site.objects.get_current().domain,
                'uid': 'uid',
                'token': 'token'
            })))
            print()

        if 'job' in selected:
            print('*** j_reminder ***')
            job_dict = base_dict({'job': job})
            print(get_email_content('j_reminder', job_dict))
            print()

            print('*** j_canceled ***')
            print(get_email_content('j_canceled', job_dict))
            print()

            print('*** j_changed ***')
            print(get_email_content('j_changed', job_dict), end='\n\n')

            job_dict['count'] = 1
            print('*** j_signup ***')
            print(get_email_content('j_signup', job_dict), end='\n\n')

            print('*** member/job/subscription_changed ***')
            print(get_template('juntagrico/mails/member/job/subscription_changed.txt').render(job_dict), end='\n\n')

            print('*** member/job/unsubscribed ***')
            print(get_template('juntagrico/mails/member/job/unsubscribed.txt').render(job_dict), end='\n\n')

            admin_job_dict = base_dict(dict(
                job=job,
                instance=job,
                member=member,
                initial_count=2,
                count=1,
                message='[Nachricht des Mitglieds]'
            ))
            print('*** admin/job/signup ***')
            print(get_template('juntagrico/mails/admin/job/signup.txt').render(admin_job_dict), end='\n\n')

            print('*** admin/job/subscription_changed ***')
            print(get_template('juntagrico/mails/admin/job/changed_subscription.txt').render(admin_job_dict), end='\n\n')

            print('*** admin/job/unsubscribed ***')
            print(get_template('juntagrico/mails/admin/job/unsubscribed.txt').render(admin_job_dict), end='\n\n')

            member_assignment_dict = base_dict(dict(
                job=job,
                instance=member,
                member=member,
                editor=co_member,
                initial_count=2,
                count=1,
                message='[Nachricht an Mitglied]'
            ))
            print('*** member/assignment/changed ***')
            print(get_template('juntagrico/mails/member/assignment/changed.txt').render(member_assignment_dict), end='\n\n')

            print('*** member/assignment/removed ***')
            print(get_template('juntagrico/mails/member/assignment/removed.txt').render(member_assignment_dict), end='\n\n')

            print('*** admin/assignment/changed ***')
            print(get_template('juntagrico/mails/admin/assignment/changed.txt').render(member_assignment_dict), end='\n\n')

            print('*** admin/assignment/removed ***')
            print(get_template('juntagrico/mails/admin/assignment/removed.txt').render(member_assignment_dict), end='\n\n')

        if 'depot' in selected:
            print('*** d_changed ***')
            print(get_email_content('d_changed', base_dict({'depot': depot})))
            print()

            print('*** juntagrico/mails/admin/depot_changed.txt ***')
            print(get_template('juntagrico/mails/admin/depot_changed.txt').render({
                'subscription': subscription,
                'member': member,
                'old_depot': depot,
                'new_depot': new_depot,
                'immediate': False,
            }), end='\n\n')

        if 'member' in selected:
            print('*** a_member_created ***')
            print(get_email_content('a_member_created', base_dict({
                'member': member
            })))
            print()

            print('*** m_canceled ***')
            print(get_email_content('m_canceled', base_dict({
                'member': member,
                'end_date': datetime.date.today(),
                'message': 'Nachricht'
            })))
            print()
