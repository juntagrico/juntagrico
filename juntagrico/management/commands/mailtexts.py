import datetime

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management

from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import get_email_content, base_dict


class Command(BaseCommand):
    help = "Prints the text of all notification emails using real data from the database, but without sending any emails."

    # entry point used by manage.py
    def handle(self, *args, **options):
        with transaction.atomic(durable=True):
            # generate temporary test data to ensure that required objects are available
            management.call_command('generate_testdata')
            subscription = Subscription.objects.all()[0]
            shares = Share.objects.all()[:2]
            job = RecuringJob.objects.all()[0]
            member, co_member = Member.objects.filter(MemberDao.has_future_subscription())[:2]
            member_wo_subs = Member.objects.filter(subscriptionmembership__isnull=True)[0]
            depot = Depot.objects.all()[0]
            transaction.set_rollback(True)  # force rollback

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

        print('*** s_created ***')

        print(get_email_content('s_created', base_dict({'shares': shares})))
        print()

        print('*** n_sub ***')

        print(get_email_content('n_sub', base_dict({'subscription': subscription, 'comment': 'user comment'})))
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

        print('*** j_reminder ***')

        print(get_email_content('j_reminder', base_dict({
            'job': job
        })))
        print()

        print('*** j_canceled ***')

        print(get_email_content('j_canceled', base_dict({'job': job})))
        print()

        print('*** confirm ***')

        print(get_email_content('confirm', base_dict({'hash': 'hash'})))
        print()

        print('*** j_changed ***')

        print(get_email_content('j_changed', base_dict({'job': job})))
        print()

        print('*** j_signup ***')

        print(get_email_content('j_signup', base_dict({'job': job})))
        print()

        print('*** d_changed ***')

        print(get_email_content('d_changed', base_dict({'depot': depot})))
        print()

        print('*** s_canceled ***')

        print(get_email_content('s_canceled', base_dict({
            'subscription': subscription,
            'message': 'Nachricht'
        })))
        print()

        print('*** a_share_created ***')

        print(get_email_content('a_share_created', base_dict({
            'share': shares[0]
        })))
        print()

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
