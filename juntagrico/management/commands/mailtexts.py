# -*- coding: utf-8 -*-

import os
import re
import hashlib

from django.contrib.auth.models import Permission, User
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone
from django.core.management.base import BaseCommand

from juntagrico.config import Config
from juntagrico.util.ical import *
from juntagrico.models import *


def get_server():
    return 'http://' + Config.adminportal_server_url()


class Command(BaseCommand):
    # entry point used by manage.py
    def handle(self, *args, **options):
        subscription = Subscription.objects.all()[0]
        if ExtraSubscription.objects.all().count() > 0:
            extrasub = ExtraSubscription.objects.all()[0]
        else:
            extrasub = None
        share = Share.objects.all()[0]
        job = RecuringJob.objects.all()[0]
        member = Member.objects.all()[0]
        depot = Depot.objects.all()[0]
        bill = Bill(ref_number='123456789', amount='1234.99')

        print('*** welcome  mit abo***')

        plaintext = get_template(Config.emails('welcome'))
        d = {
            'username': 'email@email.de',
            'password': 'password',
            'hash': 'hash',
            'subscription': subscription,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** welcome  ohne abo***')

        plaintext = get_template(Config.emails('welcome'))
        d = {
            'username': 'email@email.de',
            'password': 'password',
            'hash': 'hash',
            'subscription': None,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** s_created ***')

        plaintext = get_template(Config.emails('s_created'))
        d = {
            'share': share,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** n_sub ***')

        plaintext = get_template(Config.emails('n_sub'))
        d = {
            'subscription': subscription,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** co_welcome ***')

        plaintext = get_template(Config.emails('co_welcome'))
        d = {
            'username': 'email@email.org',
            'name': 'Hans Muster',
            'password': 'password',
            'hash': 'hash',
            'shares': '9',
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** co_added ***')

        plaintext = get_template(Config.emails('co_added'))
        d = {
            'username': 'email@email.org',
            'name': 'Hans Muster',
            'password': 'password',
            'hash': 'hash',
            'shares': '9',
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** password ***')

        plaintext = get_template(Config.emails('password'))
        d = {
            'email': 'email@email.org',
            'password': 'password',
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** j_reminder ***')

        plaintext = get_template(Config.emails('j_reminder'))
        coordinator = job.type.activityarea.coordinator
        contact = coordinator.first_name + ' ' + \
            coordinator.last_name + ': ' + job.type.activityarea.contact()
        d = {
            'job': job,
            'participants': [member],
            'serverurl': get_server(),
            'contact': contact
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** j_canceled ***')

        plaintext = get_template(Config.emails('j_canceled'))
        d = {
            'job': job,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** confirm ***')

        plaintext = get_template(Config.emails('confirm'))
        d = {
            'hash': 'hash',
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** j_changed ***')

        plaintext = get_template(Config.emails('j_changed'))
        d = {
            'job': job,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** j_signup ***')

        plaintext = get_template(Config.emails('j_signup'))
        d = {
            'job': job,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** d_changed ***')

        plaintext = get_template(Config.emails('d_changed'))
        d = {
            'depot': depot,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** s_canceled ***')

        plaintext = get_template(Config.emails('s_canceled'))
        d = {
            'subscription': subscription,
            'message': 'Nachricht',
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** m_canceled ***')

        plaintext = get_template(Config.emails('m_canceled'))
        d = {
            'member': member,
            'end_date': timezone.now(),
            'message': 'Nachricht',
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** b_share ***')

        plaintext = get_template(Config.emails('b_share'))
        d = {
            'member': member,
            'bill': bill,
            'share': share,
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        print('*** b_sub ***')

        plaintext = get_template(Config.emails('b_sub'))
        d = {
            'member': member,
            'bill': bill,
            'sub': subscription,
            'start': timezone.now(),
            'end': timezone.now(),
            'serverurl': get_server()
        }
        content = plaintext.render(d)
        print(content)
        print()

        if extrasub is not None:
            print('*** b_esub ***')

            plaintext = get_template(Config.emails('b_esub'))
            d = {
                'member': member,
                'bill': bill,
                'extrasub': extrasub,
                'start': timezone.now(),
                'end': timezone.now(),
                'serverurl': get_server()
            }
            content = plaintext.render(d)
            print(content)
            print()
