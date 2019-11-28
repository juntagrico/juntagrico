import json
import math
import ssl
import sys
import time as mytime
import urllib.error
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import TSST, TFSST, SubscriptionProduct, SubscriptionSize, SubscriptionType


class Command(BaseCommand):

    members = []
    manynames = []
    manynames_idx = 0

    def get_phone_number(self, number):
        if number < 10:
            return '079 123 45 0' + str(number)
        if number < 100:
            return '079 123 45 ' + str(number)
        if number < 1000:
            return '079 123 4' + str(number / 100) + ' ' + str(number % 100)
        return '079 123 ' + str(number / 100) + ' ' + str(number % 100)

    def get_manynames(self, N):
        cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        req = urllib.request.Request('https://uinames.com/api/?amount=' + str(N), data=None,
                                     headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        data = urllib.request.urlopen(req, context=cert)
        name_data = json.loads(data.read().decode(
            sys.stdin.encoding).encode('utf-8'))
        for person in name_data:
            name = str(person['surname'])
            prename = str(person['name'])
            email = str(slugify(prename) + '.' + slugify(name) + str(timezone.now().microsecond) + '@' + Config.info_email().split('@')[-1])
            self.manynames.append({'name': name, 'prename': prename, 'email': email})

    def get_name(self, i):
        person = self.manynames[self.manynames_idx]
        self.manynames_idx += 1
        return person

    def get_address(self, point):
        cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        url = 'https://nominatim.openstreetmap.org/reverse?lat=' + \
            str(point[1]) + '&lon=' + str(point[0]) + '&format=json'
        print(url)
        req = urllib.request.Request(
            url,
            data=None,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        f = urllib.request.urlopen(req, context=cert)
        data = f.read()
        print(json.loads(data))
        address_data = json.loads(data)['address']
        print(address_data)
        mytime.sleep(1)  # ensure rate limit on nominatim lookup
        result = {'strasselang': 'Backupstrasse', 'hnr': '42', 'plz': '8001', 'ort': 'Zürich'}
        if 'road' in address_data:
            result['strasselang'] = address_data['road']
        if 'house_number' in address_data:
            result['hnr'] = address_data['house_number']
        if 'postal_code' in address_data:
            result['plz'] = address_data['postal_code']
        if 'city' in address_data:
            result['ort'] = address_data['city']
        return result

    def generate_member_dict(self, props, i):
        name = self.get_name(i)
        print(props)
        result = {'first_name': name['prename'], 'last_name': name['name'], 'email': name['email'],
                  'addr_street': props['strasselang'] + ' ' + props['hnr'], 'addr_zipcode': props['plz'], 'addr_location': props['ort'],
                  'birthday': '2017-03-27', 'phone': self.get_phone_number(i), 'mobile_phone': '', 'confirmed': True,
                  'reachable_by_email': False}
        print(result)
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

    def generate_depot(self, props, member, i, coordinates):
        depot_dict = {'code': 'D' + str(i), 'name': props['betriebsname'], 'weekday': 2, 'latitude': str(coordinates[1]),
                      'longitude': str(coordinates[0]), 'addr_street': props['strasselang'] + ' ' + props['hnr'], 'addr_zipcode': props['plz'],
                      'addr_location': props['ort'], 'description': 'Hinter dem Restaurant ' + props['betriebsname'], 'contact': member}
        depot = Depot.objects.create(**depot_dict)
        return depot

    def generate_subscription(self, main_member, co_member, depot, type):
        sub_dict = {'depot': depot, 'future_depot': None, 'active': True,
                    'activation_date': '2017-03-27', 'deactivation_date': None, 'creation_date': '2017-03-27',
                    'start_date': '2018-01-01'}
        subscription = Subscription.objects.create(**sub_dict)
        main_member.subscription = subscription
        main_member.save()
        co_member.subscription = subscription
        co_member.save()
        subscription.primary_member = main_member
        subscription.save()
        self.members.append(main_member)
        self.members.append(co_member)
        TSST.objects.create(type=type, subscription=subscription)
        TFSST.objects.create(type=type, subscription=subscription)

    def generate_depot_sub(self, depot, coordinates, j, sub_shares, type):
        props = self.get_address(coordinates)
        mem1_fields = self.generate_member_dict(props, j)
        main_member = Member.objects.create(**mem1_fields)
        self.generate_shares(main_member, sub_shares)
        mem2_fields = self.generate_member_dict(props, j)
        co_member = Member.objects.create(**mem2_fields)
        self.generate_shares(main_member, sub_shares)
        self.generate_subscription(main_member, co_member, depot, type)

    # entry point used by manage.py
    def handle(self, *args, **options):
        cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

        subprod_field = {'name': 'Gemüse'}
        sub_product, created = SubscriptionProduct.objects.get_or_create(**subprod_field)

        sub_size = int(input('Size of subscription? [2] ') or 2)
        sub_shares = int(input('Required shares per subscription? [2] ') or 2)
        sub_assignments = int(input('Required assignment per subscription? [6] ') or 6)
        sub_prize = int(input('Price of subscription? [250] ') or 250)
        depots_to_generate = int(input('Number of depots to generate? [4] ') or 4)
        subs_per_depot = int(input('Number of supscriptions per depot? [10] ') or 10)
        job_amount = int(input('Jobs per area? [10] ') or 10)
        self.get_manynames(500)  # Get 500 fake names (max number per API call)

        subsize_fields = {'name': 'Normales Abo', 'long_name': 'Ganz Normales Abo', 'units': sub_size,
                          'depot_list': True,
                          'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen Zwei personen Haushalt für eine Woche.',
                          'product': sub_product}
        size = SubscriptionSize.objects.create(**subsize_fields)

        subtype_fields = {'name': 'Normales Abo typ', 'long_name': '', 'shares': sub_shares, 'required_assignments': sub_assignments, 'price': sub_prize,
                          'description': '', 'size': size}

        type = SubscriptionType.objects.create(**subtype_fields)

        req = urllib.request.urlopen(
            # This URL breaks regularly, look it up under https://data.stadt-zuerich.ch "Gastwirtschaftsbetriebe"
            'https://data.stadt-zuerich.ch/dataset/5704b4a1-d7ee-4c20-bd16-f194f6bb1d8c/resource/095b5f70-85cb-43c9-884f-630e4fb0e86d/download/gastwirtschaftsbetriebe_per_20181231.json', context=cert)
        depot_data = json.loads(req.read())['features']

        req = urllib.request.urlopen(
            'https://data.stadt-zuerich.ch/dataset/brunnen/resource/d741cf9c-63be-495f-8c3e-9418168fcdbf/download/brunnen.json', context=cert)
        address_data = json.loads(req.read())['features']
        adress_counter = 0
        amount_of_depots = len(depot_data)
        depots_to_generate = min(amount_of_depots, depots_to_generate)
        depots_to_generate = max(1, depots_to_generate)

        for i in range(0, depots_to_generate):
            props = depot_data[i]['properties']
            mem1_fields = self.generate_member_dict(props, i)
            main_member = Member.objects.create(**mem1_fields)
            self.generate_shares(main_member, sub_shares)
            depot = self.generate_depot(
                props, main_member, i, depot_data[i]['geometry']['coordinates'][0])
            mem2_fields = self.generate_member_dict(props, i)
            co_member = Member.objects.create(**mem2_fields)
            self.generate_shares(main_member, sub_shares)
            self.generate_subscription(main_member, co_member, depot, type)
            for j in range(1, subs_per_depot):
                self.generate_depot_sub(
                    depot, address_data[adress_counter]['geometry']['coordinates'], j, sub_shares, type)
                adress_counter += 1

        area1_fields = {'name': 'Ernten', 'description': 'Das Gemüse aus der Erde Ziehen', 'core': True,
                        'hidden': False, 'coordinator': self.members[0], 'show_coordinator_phonenumber': False}
        area2_fields = {'name': 'Jäten', 'description': 'Das Unkraut aus der Erde Ziehen', 'core': False,
                        'hidden': False, 'coordinator': self.members[1], 'show_coordinator_phonenumber': False}
        area_1 = ActivityArea.objects.create(**area1_fields)
        if len(self.members) > 2:
            area_1.members.set(self.members[2:int((len(self.members)) / 2)])
        else:
            area_1.members.set(self.members)
        area_1.save()
        area_2 = ActivityArea.objects.create(**area2_fields)
        if len(self.members) > 2:
            area_2.members.set(self.members[int(
                (len(self.members)) / 2) + 1:int((len(self.members)) / 2 - 1)])
        else:
            area_2.members.set(self.members)
        area_2.save()
        type1_fields = {'name': 'Ernten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_1,
                        'duration': 2, 'location': 'auf dem Hof'}
        type2_fields = {'name': 'Jäten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_2,
                        'duration': 2, 'location': 'auf dem Hof'}
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_1}
        for x in range(0, job_amount):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job1_all_fields)

        job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_2}
        for x in range(0, job_amount):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job2_all_fields)
