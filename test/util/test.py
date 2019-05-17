from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob, Assignment
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType, TSST, TFSST


class JuntagricoTestCase(TestCase):
    
    def setUp(self):
        """
            member
            """
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': 'test@email.org',
                       'addr_street': 'addr_street',
                       'addr_zipcode': 'addr_zipcode',
                       'addr_location': 'addr_location',
                       'phone': 'phone',
                       'confirmed': True,
                       }
        self.member = Member.objects.create(**member_data)
        self.member.user.set_password("12345")
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_depot_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_subscriptions'))
        self.member.user.save()
        """
        shares
        """
        self.share_data = {'member': self.member,
                           'paid_date': '2017-03-27',
                           'issue_date': '2017-03-27',
                           'booking_date': None,
                           'cancelled_date': None,
                           'termination_date': None,
                           'payback_date': None,
                           'number': None,
                           'notes': ''
                           }
        Share.objects.create(**self.share_data)
        """
        area
        """
        area_data = {'name': 'name',
                     'coordinator': self.member}
        self.area = ActivityArea.objects.create(**area_data)
        """
        job_type
        """
        job_type_data = {'name': 'name',
                         'activityarea': self.area,
                         'duration': 2}
        self.job_type = JobType.objects.create(**job_type_data)
        """
        jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        job_data = {'slots': 1,
                    'time': time,
                    'type': self.job_type}
        self.job1 = RecuringJob.objects.create(**job_data)
        self.job2 = RecuringJob.objects.create(**job_data)
        """
        assignment
        """
        assignment_data = {'job': self.job2,
                           'member': self.member,
                           'amount': 1}
        Assignment.objects.create(**assignment_data)
        """
        depots
        """
        depot_data = {
            'code': 'c1',
            'name': 'depot',
            'contact': self.member,
            'weekday': 1}
        self.depot = Depot.objects.create(**depot_data)
        depot_data = {
            'code': 'c2',
            'name': 'depot2',
            'contact': self.member,
            'weekday': 1}
        self.depot2 = Depot.objects.create(**depot_data)
        """
        subscription product, size and types
        """
        sub_product_data = {
            'name': 'product'
        }
        self.sub_product = SubscriptionProduct.objects.create(**sub_product_data)
        sub_size_data = {
            'name': 'sub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': self.sub_product,
            'description': 'sub_desc'
        }
        self.sub_size = SubscriptionSize.objects.create(**sub_size_data)
        sub_type_data = {
            'name': 'sub_type_name',
            'long_name': 'sub_type_long_name',
            'size': self.sub_size,
            'shares': 1,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.sub_type = SubscriptionType.objects.create(**sub_type_data)
        sub_type_data = {
            'name': 'sub_type_name2',
            'long_name': 'sub_type_long_name',
            'size': self.sub_size,
            'shares': 2,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.sub_type2 = SubscriptionType.objects.create(**sub_type_data)
        """
        subscription
        """
        sub_data = {'depot': self.depot,
                    'future_depot': None,
                    'active': True,
                    'activation_date': '2017-03-27',
                    'deactivation_date': None,
                    'creation_date': '2017-03-27',
                    'start_date': '2018-01-01',
                    'primary_member': self.member
        }
        self.sub = Subscription.objects.create(**sub_data)
        self.member.subscription = self.sub
        self.member.save()
        TSST.objects.create(subscription=self.sub, type=self.sub_type)
        TFSST.objects.create(subscription=self.sub, type=self.sub_type)

    def assertSimpleGet(self, url):
        self.client.force_login(self.member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def assertSimplePost(self, url, data):
        self.client.force_login(self.member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
