# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.models import *


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        mem1_fields = {'first_name': 'Boro', 'last_name': 'Sadler', 'email': 'boro.sadler@juntagrico.juntagrico',
                       'addr_street': 'Mühlezelgstrasse 1', 'addr_zipcode': '8047', 'addr_location': 'Zürich',
                       'birthday': '2017-03-27', 'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False, 'block_emails': False}
        mem2_fields = {'first_name': 'Deepak', 'last_name': 'Olvirsson',
                       'email': 'deepak.olvirsson@juntagico.juntagrico', 'addr_street': 'Otto-Lang-Weg 1',
                       'addr_zipcode': '8044', 'addr_location': 'Zürich', 'birthday': '2017-03-27',
                       'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False, 'block_emails': False}
        member_1 = Member.objects.create(**mem1_fields)
        member_2 = Member.objects.create(**mem2_fields)
        share_all_fields = {'member': member_1, 'paid_date': '2017-03-27', 'issue_date': '2017-03-27', 'booking_date': None,
                            'cancelled_date': None, 'termination_date': None, 'payback_date': None, 'number': None,
                            'notes': ''}
        Share.objects.create(**share_all_fields)
        Share.objects.create(**share_all_fields)
        share_all_fields['member'] = member_2
        Share.objects.create(**share_all_fields)
        Share.objects.create(**share_all_fields)
        subsize_fields = {'name': 'Normales Abo', 'long_name': 'Ganz Normales Abo', 'size': 1, 'shares': 2,
                          'depot_list': True, 'required_assignments': 10, 'price': 1000,
                          'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen Zwei personen Haushalt für eine Woche.'}
        SubscriptionSize.objects.create(**subsize_fields)
        depot1_fields = {'code': 'D1', 'name': 'Toblerplatz', 'weekday': 2, 'latitude': '47.379308',
                         'longitude': '8.559405', 'addr_street': 'Toblerstrasse 73', 'addr_zipcode': '8044',
                         'addr_location': 'Zürich', 'description': 'Hinter dem Migros', 'contact': member_2}
        depot2_fields = {'code': 'D2', 'name': 'Siemens', 'weekday': 4, 'latitude': '47.379173',
                         'longitude': '8.495392', 'addr_street': 'Albisriederstrasse 207', 'addr_zipcode': '8047',
                         'addr_location': 'Zürich', 'description': 'Hinter dem Restaurant Cube', 'contact': member_1}
        depot1 = Depot.objects.create(**depot1_fields)
        depot2 = Depot.objects.create(**depot2_fields)
        sub_1_fields = {'depot': depot1, 'future_depot': None, 'size': 1, 'future_size': 1, 'active': True,
                        'activation_date': '2017-03-27', 'deactivation_date': None, 'creation_date': '2017-03-27',
                        'start_date': '2018-01-01'}
        sub_2_fields = {'depot': depot2, 'future_depot': None, 'size': 1, 'future_size': 1,
                        'active': True, 'activation_date': '2017-03-27', 'deactivation_date': None,
                        'creation_date': '2017-03-27', 'start_date': '2018-01-01'}
        subscription_1 = Subscription.objects.create(**sub_1_fields)
        member_1.subscription = subscription_1
        member_1.save()
        subscription_2 = Subscription.objects.create(**sub_2_fields)
        member_2.subscription = subscription_2
        member_2.save()
        area1_fields = {'name': 'Ernten', 'description': 'Das Gemüse aus der Erde Ziehen', 'core': True,
                        'hidden': False, 'coordinator': member_1, 'show_coordinator_phonenumber': False}
        area2_fields = {'name': 'Jäten', 'description': 'Das Unkraut aus der Erde Ziehen', 'core': False,
                        'hidden': False, 'coordinator': member_2, 'show_coordinator_phonenumber': False}
        area_1 = ActivityArea.objects.create(**area1_fields)
        area_1.members = [member_2]
        area_1.save()
        area_2 = ActivityArea.objects.create(**area2_fields)
        area_2.members = [member_1]
        area_2.save()
        type1_fields = {'name': 'Ernten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_1,
                        'duration': 2, 'location': 'auf dem Hof'}
        type2_fields = {'name': 'Jäten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_2,
                        'duration': 2, 'location': 'auf dem Hof'}
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_1}
        for x in range(0, 10):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job1_all_fields)

        job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_2}
        for x in range(0, 10):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job2_all_fields)
