import math

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType

fake = Faker()


class Command(BaseCommand):
    members = []

    def generate_member_dict(self, props):
        checked_email = fake.email()
        while 0 != Member.objects.filter(email=checked_email).count():
            checked_email = fake.email()
        result = {
            'birthday': fake.date(),
            'confirmed': True,
            'email': checked_email,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'mobile_phone': '',
            'phone': fake.phone_number(),
            'reachable_by_email': False,
        }

        # Update with input from props
        result.update({
            'addr_street': '{} {}'.format(props['strasselang'], props['hnr']),
            'addr_zipcode': props['plz'],
            'addr_location': props['ort'],
        })

        return result

    def generate_share_dict(self, member):
        result = {'member': member, 'paid_date': '2017-03-27', 'issue_date': '2017-03-27', 'booking_date': None,
                  'cancelled_date': None, 'termination_date': None, 'payback_date': None, 'number': None,
                  'notes': ''}
        return result

    def generate_shares(self, member, sub_share):
        amount = int(math.ceil(float(sub_share) / 2.0))
        for i in range(0, amount):
            share_dict = self.generate_share_dict(member)
            Share.objects.create(**share_dict)

    def generate_depot(self, props, member, i):
        depot_dict = {
            'contact': member,
            'description': fake.random_element(elements=[
                'Hinter dem Restaurant'
                'Unter der Treppe',
                'Beim Friseur'
            ]),
            'name': fake.company(),
            'weekday': fake.random_int(0, 6),
            'latitude': fake.latitude(),
            'longitude': fake.longitude(),
        }
        depot_dict.update({
            'addr_street': '{} {}'.format(props['strasselang'], props['hnr']),
            'addr_zipcode': props['plz'],
            'addr_location': props['ort'],
        })
        depot, _ = Depot.objects.update_or_create(**depot_dict)
        return depot

    def generate_subscription(self, main_member, co_member, depot, type):
        sub_dict = {
            'depot': depot,
            'future_depot': None,
            'creation_date': fake.date_between(start_date='-10y', end_date='-1m')
        }
        sub_dict['activation_date'] = sub_dict['creation_date']
        subscription = Subscription.objects.create(**sub_dict)
        subscription.primary_member = main_member
        subscription.subscriptionmembership_set.create(
            member=main_member,
            join_date=sub_dict['creation_date'])
        subscription.subscriptionmembership_set.create(
            member=co_member,
            join_date=sub_dict['creation_date'])
        subscription.save()
        self.members.append(main_member)
        self.members.append(co_member)

    def get_random_props(self):
        return {
            'strasselang': fake.street_name(),
            'hnr': fake.random_element(elements=list(range(1, 421)) + [
                '13a',
                '12c',
                '129a',
                '161b'
            ]),
            'plz': fake.postcode(),
            'ort': fake.city()
        }

    def generate_depot_sub(self, depot, sub_shares, type):
        props = self.get_random_props()
        mem1_fields = self.generate_member_dict(props)
        main_member = Member.objects.create(**mem1_fields)
        self.generate_shares(main_member, sub_shares)
        mem2_fields = self.generate_member_dict(props)
        co_member = Member.objects.create(**mem2_fields)
        self.generate_shares(main_member, sub_shares)
        self.generate_subscription(main_member, co_member, depot, type)

    def add_arguments(self, parser):
        parser.add_argument('--sub-size', type=int, help='Size of subscription', default=2)
        parser.add_argument('--sub-shares', type=int, help='Required shares per subscription', default=2)
        parser.add_argument('--sub-assignments', type=int, help='Required assignment per subscription', default=6)
        parser.add_argument('--sub-prize', type=int, help='Proce of suscription', default=250)
        parser.add_argument('--depots', type=int, help='Number of depots to generate', default=4)
        parser.add_argument('--subs-per-depot', type=int, help='Subscriptions per depot', default=10)
        parser.add_argument('--job-amount', type=int, help='Jobs per area', default=10)

    # entry point used by manage.py
    def handle(self, *args, **options):
        subprod_field = {'name': 'Gemüse'}
        sub_product, created = SubscriptionProduct.objects.get_or_create(**subprod_field)

        subsize_fields = {'name': 'Normales Abo', 'long_name': 'Ganz Normales Abo', 'units': options['sub_size'],
                          'depot_list': True,
                          'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen Zwei personen Haushalt für eine Woche.',
                          'product': sub_product}
        size, _ = SubscriptionSize.objects.get_or_create(**subsize_fields)

        subtype_fields = {
            'name': 'Normales Abo typ',
            'long_name': '',
            'shares': options['sub_shares'],
            'required_assignments': options['sub_assignments'],
            'price': options['sub_prize'],
            'description': '',
            'size': size
        }
        type, _ = SubscriptionType.objects.get_or_create(
            name=subtype_fields['name'],
            defaults=subtype_fields
        )

        for i in range(0, options['depots']):
            props = self.get_random_props()

            mem1_fields = self.generate_member_dict(props)
            main_member = Member.objects.create(**mem1_fields)
            self.generate_shares(main_member, options['sub_shares'])
            depot = self.generate_depot(props, main_member, i)
            mem2_fields = self.generate_member_dict(props)
            co_member = Member.objects.create(**mem2_fields)
            self.generate_shares(co_member, options['sub_shares'])
            self.generate_subscription(main_member, co_member, depot, type)
            for _ in range(1, options['subs_per_depot']):
                self.generate_depot_sub(depot, options['sub_shares'], type)

        area1_fields = {'name': 'Ernten', 'description': 'Das Gemüse aus der Erde Ziehen', 'core': True,
                        'hidden': False, 'coordinator': self.members[0], 'show_coordinator_phonenumber': False}
        area2_fields = {'name': 'Jäten', 'description': 'Das Unkraut aus der Erde Ziehen', 'core': False,
                        'hidden': False, 'coordinator': self.members[1], 'show_coordinator_phonenumber': False}
        area_1, _ = ActivityArea.objects.get_or_create(
            name=area1_fields['name'],
            defaults=area1_fields
        )
        if len(self.members) > 2:
            area_1.members.set(self.members[2:int((len(self.members)) / 2)])
        else:
            area_1.members.set(self.members)
        area_1.save()
        area_2, _ = ActivityArea.objects.get_or_create(
            name=area2_fields['name'],
            defaults=area2_fields
        )
        if len(self.members) > 2:
            area_2.members.set(self.members[int(
                (len(self.members)) / 2) + 1:int((len(self.members)) / 2 - 1)])
        else:
            area_2.members.set(self.members)
        area_2.save()
        type1_fields = {'name': 'Ernten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_1,
                        'default_duration': 2, 'location': 'auf dem Hof'}
        type2_fields = {'name': 'Jäten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_2,
                        'default_duration': 2, 'location': 'auf dem Hof'}
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_1}
        for x in range(0, options['job_amount']):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job1_all_fields)

        job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_2}
        for x in range(0, options['job_amount']):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job2_all_fields)
