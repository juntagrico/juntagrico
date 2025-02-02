import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob
from juntagrico.entity.location import Location
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


class Command(BaseCommand):
    help = "Generate test data for development environments. DO NOT USE IN PRODUCTION."

    @staticmethod
    def create_subscription(depot, member, subtype, activation_date=None,):
        sub_fields = {'depot': depot, 'future_depot': None,
                      'activation_date': activation_date,
                      'deactivation_date': None, 'creation_date': '2017-03-27', 'start_date': '2018-01-01'}
        subscription = Subscription.objects.create(**sub_fields)
        member.leave_subscription(changedate=datetime.date.today() - datetime.timedelta(1))
        if member.subscription_future:
            member.leave_subscription(member.subscription_future)
        member.join_subscription(subscription)
        subscription.primary_member = member
        subscription.save()
        SubscriptionPart.objects.create(subscription=subscription, type=subtype,
                                        activation_date=activation_date)

    # entry point used by manage.py
    def handle(self, *args, **options):
        settings.TMP_DISABLE_EMAILS = True  # prevent sending emails while creating testdata
        try:
            mem1_fields = {'first_name': 'Boro', 'last_name': 'Sadler', 'email': 'boro.sadler@juntagrico.juntagrico',
                           'addr_street': 'Mühlezelgstrasse 1', 'addr_zipcode': '8047', 'addr_location': 'Zürich',
                           'birthday': '2017-03-27', 'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                           'reachable_by_email': False}
            mem2_fields = {'first_name': 'Deepak', 'last_name': 'Olvirsson',
                           'email': 'deepak.olvirsson@juntagico.juntagrico', 'addr_street': 'Otto-Lang-Weg 1',
                           'addr_zipcode': '8044', 'addr_location': 'Zürich', 'birthday': '2017-03-27',
                           'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                           'reachable_by_email': False}
            mem3_fields = {'first_name': 'Isabella', 'last_name': 'Sundberg',
                           'email': 'isabella.sundberg@juntagico.juntagrico', 'addr_street': 'Holunderhof 5',
                           'addr_zipcode': '8050', 'addr_location': 'Zürich', 'birthday': '2022-02-02',
                           'phone': '079 987 78 50', 'mobile_phone': '', 'confirmed': True,
                           'reachable_by_email': False}
            mem4_fields = {'first_name': 'Madeleine', 'last_name': 'Ljungborg',
                           'email': 'madeleine.ljungborg@juntagico.juntagrico', 'addr_street': 'Erlachstrasse 39',
                           'addr_zipcode': '8003', 'addr_location': 'Zürich', 'birthday': '2022-02-02',
                           'phone': '076 987 78 50', 'mobile_phone': '', 'confirmed': True,
                           'reachable_by_email': False}
            mem5_fields = {'first_name': 'Jessica', 'last_name': 'Van den Akker',
                           'email': 'jessica.akker@juntagico.juntagrico', 'addr_street': 'Kasinostrasse 10',
                           'addr_zipcode': '8032', 'addr_location': 'Zürich', 'birthday': '2022-02-02',
                           'phone': '076 927 78 55', 'mobile_phone': '', 'confirmed': True,
                           'reachable_by_email': False}
            member_1, _ = Member.objects.get_or_create(email=mem1_fields['email'], defaults=mem1_fields)
            member_2, _ = Member.objects.get_or_create(email=mem2_fields['email'], defaults=mem2_fields)
            member_3, _ = Member.objects.get_or_create(email=mem3_fields['email'], defaults=mem3_fields)
            member_4, _ = Member.objects.get_or_create(email=mem4_fields['email'], defaults=mem4_fields)
            Member.objects.get_or_create(email=mem5_fields['email'], defaults=mem5_fields)
            if Config.enable_shares():
                share_all_fields = {'member': member_1, 'paid_date': '2017-03-27', 'issue_date': '2017-03-27', 'booking_date': None,
                                    'cancelled_date': None, 'termination_date': None, 'payback_date': None, 'number': None,
                                    'notes': ''}
                Share.objects.create(**share_all_fields)
                Share.objects.create(**share_all_fields)
                share_all_fields['member'] = member_2
                Share.objects.create(**share_all_fields)
                Share.objects.create(**share_all_fields)
                share_all_fields['member'] = member_3
                Share.objects.create(**share_all_fields)
            subproduct, _ = SubscriptionProduct.objects.get_or_create(name='Gemüse')
            subsize_name = 'Normales Abo'
            subsize_fields = {'long_name': 'Ganz Normales Abo', 'units': 1, 'visible': True, 'depot_list': True,
                              'product': subproduct,
                              'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen '
                                             'Zwei personen Haushalt für eine Woche.'}
            subsize = SubscriptionSize.objects.filter(
                Q(units=subsize_fields['units']) | Q(name=subsize_name), product=subsize_fields['product']
            ).first()
            if not subsize:
                subsize = SubscriptionSize.objects.create(**subsize_fields)
            subtype_fields = {'name': 'Normales Abo', 'long_name': 'Ganz Normales Abo', 'size': subsize, 'shares': 2,
                              'visible': True, 'required_assignments': 10, 'price': 1000,
                              'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen '
                                             'Zwei personen Haushalt für eine Woche.'}
            subtype, _ = SubscriptionType.objects.get_or_create(name=subtype_fields['name'], defaults=subtype_fields)
            depot1_location_fields = {'name': 'Depot Toblerplatz', 'latitude': '47.379308',
                                      'longitude': '8.559405', 'addr_street': 'Toblerstrasse 73', 'addr_zipcode': '8044',
                                      'addr_location': 'Zürich'}
            depot1_location, _ = Location.objects.get_or_create(name=depot1_location_fields['name'],
                                                                defaults=depot1_location_fields)
            depot1_location.save()
            depot2_location_fields = {'name': 'Depot Siemens', 'latitude': '47.379173',
                                      'longitude': '8.495392', 'addr_street': 'Albisriederstrasse 207',
                                      'addr_zipcode': '8047',
                                      'addr_location': 'Zürich'}
            depot2_location, _ = Location.objects.get_or_create(name=depot2_location_fields['name'],
                                                                defaults=depot2_location_fields)
            depot2_location.save()
            depot1_fields = {'name': 'Toblerplatz', 'weekday': 2, 'location': depot1_location,
                             'description': 'Hinter dem Migros', 'contact': member_2}
            depot2_fields = {'name': 'Siemens', 'weekday': 4, 'location': depot2_location,
                             'description': 'Hinter dem Restaurant Cube', 'contact': member_1}
            depot1, _ = Depot.objects.get_or_create(name=depot1_fields['name'], defaults=depot1_fields)
            depot2, _ = Depot.objects.get_or_create(name=depot2_fields['name'], defaults=depot2_fields)

            self.create_subscription(depot1, member_1, subtype, datetime.datetime.strptime('27/03/17', '%d/%m/%y').date())
            self.create_subscription(depot2, member_2, subtype, datetime.datetime.strptime('27/03/17', '%d/%m/%y').date())
            self.create_subscription(depot1, member_3, subtype)
            self.create_subscription(depot2, member_4, subtype)

            area1_fields = {'name': 'Ernten', 'description': 'Das Gemüse aus der Erde Ziehen', 'core': True,
                            'hidden': False, 'coordinator': member_1,
                            'auto_add_new_members': True}
            area2_fields = {'name': 'Jäten', 'description': 'Das Unkraut aus der Erde Ziehen', 'core': False,
                            'hidden': False, 'coordinator': member_2,
                            'auto_add_new_members': False}
            area_1, _ = ActivityArea.objects.get_or_create(name=area1_fields['name'], defaults=area1_fields)
            area_1.members.set([member_2])
            area_1.save()
            area_2, _ = ActivityArea.objects.get_or_create(name=area2_fields['name'], defaults=area2_fields)
            area_2.members.set([member_1])
            area_2.save()

            location_1_fields = {'name': 'auf dem Hof'}
            location_1, _ = Location.objects.get_or_create(**location_1_fields)
            location_1.save()

            type1_fields = {'name': 'Ernten', 'displayed_name': '', 'description': 'Ein Einsatz auf dem Feld',
                            'activityarea': area_1, 'default_duration': 2, 'location': location_1}
            type2_fields = {'name': 'Jäten', 'displayed_name': '', 'description': 'Ein Einsatz auf dem Feld',
                            'activityarea': area_2, 'default_duration': 2, 'location': location_1}
            type_1, _ = JobType.objects.get_or_create(name=type1_fields['name'], defaults=type1_fields)
            type_2, _ = JobType.objects.get_or_create(name=type2_fields['name'], defaults=type2_fields)
            job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                               'canceled': False, 'type': type_1}
            for _ in range(0, 10):
                job1_all_fields['time'] += timezone.timedelta(days=7)
                RecuringJob.objects.create(**job1_all_fields)

            job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                               'canceled': False, 'type': type_2}
            for _ in range(0, 10):
                job1_all_fields['time'] += timezone.timedelta(days=7)
                RecuringJob.objects.create(**job2_all_fields)
        finally:
            del settings.TMP_DISABLE_EMAILS
