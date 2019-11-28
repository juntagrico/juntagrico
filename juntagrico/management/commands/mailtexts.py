from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.util.mailer import get_email_content, base_dict


def get_server():
    return 'http://' + Config.adminportal_server_url()


class Command(BaseCommand):
    # entry point used by manage.py
    def handle(self, *args, **options):
        subscription = Subscription.objects.all()[0]
        shares = Share.objects.all()[:2]
        job = RecuringJob.objects.all()[0]
        member = Member.objects.all()[0]
        co_member = Member.objects.filter(subscription__isnull=False)[0]
        depot = Depot.objects.all()[0]

        print('*** welcome  mit abo***')

        print(get_email_content('welcome', base_dict({
            'member': member,
            'password': 'password',
            'subscription': subscription
        })))
        print()

        print('*** welcome  ohne abo***')

        print(get_email_content('welcome', base_dict({
            'member': member,
            'password': 'password',
            'subscription': None
        })))
        print()

        print('*** s_created ***')

        print(get_email_content('s_created', base_dict({'shares': shares})))
        print()

        print('*** n_sub ***')

        print(get_email_content('n_sub', base_dict({'subscription': subscription})))
        print()

        print('*** co_welcome ***')

        print(get_email_content('co_welcome', base_dict({
            'co_member': co_member,
            'password': 'password'
        })))
        print()

        print('*** co_added ***')

        print(get_email_content('co_added', base_dict({
            'co_member': co_member,
            'password': 'password',
            'new_shares': '9'
        })))
        print()

        print('*** password ***')

        print(get_email_content('password', base_dict({
            'email': 'email@email.org',
            'password': 'password',
        })))
        print()

        print('*** j_reminder ***')

        contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
        print(get_email_content('j_reminder', base_dict({
            'job': job,
            'participants': [member],
            'contact': contact
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
            'end_date': timezone.now(),
            'message': 'Nachricht'
        })))
        print()
