# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
import math
import sys

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.defaultfilters import slugify

from juntagrico.models import *
from juntagrico.config import Config


class Command(BaseCommand):

    members = []

    def get_phone_number(self, number):
        if number < 10:
            return '079 123 45 0'+str(number)
        if number < 100:
            return '079 123 45 '+str(number)
        if number < 1000:
            return '079 123 4'+str(number/100)+' '+str(number % 100)
        return '079 123 '+str(number/100)+' '+str(number % 100)

    def get_name(self, i):
        cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        req = urllib.request.urlopen('https://uinames.com/api/', context=cert)
        name_data = json.loads(req.read().decode(
            sys.stdin.encoding).encode('utf-8'))
        name = str(name_data['surname'])
        prename = str(name_data['name'])
        email = str(slugify(prename)+'.'+slugify(name)+str(i) +
                    str(timezone.now().microsecond)+'@'+Config.info_email().split('@')[-1])
        return {'name': name, 'prename': prename, 'email': email}

    def get_address(self, point):
        latlng = str(point[1])+','+str(point[0])
        cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + \
            latlng+'&key='+Config.google_api_key()
        print(url)
        req = urllib.request.urlopen(url, context=cert)
        data = req.read()
        address_data = json.loads(data)['results'][0]['address_components']
        print(address_data)
        result = {'HNr': ''}
        for item in address_data:
            if 'route' in item['types']:
                result['StrasseLan'] = item['long_name']
            elif 'street_number' in item['types']:
                result['HNr'] = item['long_name']
            elif 'postal_code' in item['types']:
                result['PLZ'] = item['long_name']
            elif 'locality' in item['types']:
                result['Ort'] = item['long_name']
        return result

    def generate_member_dict(self, props, i):
        name = self.get_name(i)
        result = {'first_name': name['prename'], 'last_name': name['name'], 'email': name['email'],
                  'addr_street': props['StrasseLan'] + ' ' + props['HNr'], 'addr_zipcode': props['PLZ'], 'addr_location': props['Ort'],
                  'birthday': '2017-03-27', 'phone': self.get_phone_number(i), 'mobile_phone': '', 'confirmed': True,
                  'reachable_by_email': False, 'block_emails': False}
        print(result)
        return result

    def generate_share_dict(self, member):
        result = {'member': member, 'paid_date': '2017-03-27', 'issue_date': '2017-03-27', 'booking_date': None,
                  'cancelled_date': None, 'termination_date': None, 'payback_date': None, 'number': None,
                  'notes': ''}
        return result

    def generate_shares(self, member, sub_share):
        amount = int(math.ceil(float(sub_share)/2.0))
        for i in range(0, amount):
            share_dict = self.generate_share_dict(member)
            Share.objects.create(**share_dict)

    def generate_depot(self, props, member, i, coordinates):
        depot_dict = {'code': 'D'+str(i), 'name': props['Betriebsna'], 'weekday': 2, 'latitude': str(coordinates[1]),
                      'longitude': str(coordinates[0]), 'addr_street': props['StrasseLan'] + ' ' + props['HNr'], 'addr_zipcode': props['PLZ'],
                      'addr_location': props['Ort'], 'description': 'Hinter dem Restaurant '+props['Betriebsna'], 'contact': member}
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

        sub_size = int(eval(input('Size of subscription (a number)')))
        sub_shares = int(
            eval(input('Required shares per subscription (a number)')))
        sub_assignments = int(
            eval(input('Required assignment per subscription (a number)')))
        sub_prize = int(eval(input('Price of subscription (a number)')))
        subsize_fields = {'name': 'Normales Abo', 'long_name': 'Ganz Normales Abo', 'size': sub_size,
                          'depot_list': True,
                          'description': 'Das einzige abo welches wir haben, bietet genug Gemüse für einen Zwei personen Haushalt für eine Woche.'}
        size = SubscriptionSize.objects.create(**subsize_fields)

        subtype_fields = {'name': 'Normales Abo typ', 'long_name': '', 'shares': sub_shares, 'required_assignments': sub_assignments, 'price': sub_prize,
                          'description': '', 'size': size}

        type = SubscriptionType.objects.create(**subtype_fields)

        req = urllib.request.urlopen(
            'https://data.stadt-zuerich.ch/dataset/b2c829d4-9d4b-4741-a944-242c28f00b2a/resource/0119385c-52d4-4dfb-a18f-8c6178a16460/download/gastwirtschaftsbetriebeper20161231.json', context=cert)
        req.read(3)  # source is shitty
        depot_data = json.loads(req.read())['features']

        req = urllib.request.urlopen(
            'https://data.stadt-zuerich.ch/dataset/brunnen/resource/d741cf9c-63be-495f-8c3e-9418168fcdbf/download/brunnen.json', context=cert)
        address_data = json.loads(req.read())['features']
        adress_counter = 0

        amount_of_depots = len(depot_data)
        depots_to_generate = int(eval(
            input('Number of depots to generate (max :'+str(amount_of_depots)+' min: 1)')))
        depots_to_generate = min(amount_of_depots, depots_to_generate)
        depots_to_generate = max(1, depots_to_generate)
        subs_per_depot = int(eval(input('supscriptions per depot (a number)')))

        for i in range(0, depots_to_generate):
            props = depot_data[i]['properties']
            mem1_fields = self.generate_member_dict(props, i)
            main_member = Member.objects.create(**mem1_fields)
            self.generate_shares(main_member, sub_shares)
            depot = self.generate_depot(
                props, main_member, i, depot_data[i]['geometry']['coordinates'])
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
            area_1.members = self.members[2:int((len(self.members))/2)]
        else:
            area_1.members = [self.members[1]]
        area_1.save()
        area_2 = ActivityArea.objects.create(**area2_fields)
        if len(self.members) > 2:
            area_2.members = self.members[int(
                (len(self.members))/2)+1:int((len(self.members))/2-1)]
        else:
            area_2.members = [self.members[0]]
        area_2.save()
        type1_fields = {'name': 'Ernten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_1,
                        'duration': 2, 'location': 'auf dem Hof'}
        type2_fields = {'name': 'Jäten', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_2,
                        'duration': 2, 'location': 'auf dem Hof'}
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_1}
        job_amount = int(eval(input('Jobs per area (a number)')))
        for x in range(0, job_amount):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job1_all_fields)

        job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_2}
        for x in range(0, job_amount):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job2_all_fields)
