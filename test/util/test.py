from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob, Assignment, OneTimeJob
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType, TSST, TFSST


class JuntagricoTestCase(TestCase):

    def setUp(self):
        self.set_up_member()
        self.set_up_shares()
        self.set_up_job()
        self.set_up_sub()

    def set_up_member(self):
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
        member_data2 = {'first_name': 'first_name2',
                        'last_name': 'last_name2',
                        'email': 'test2@email.org',
                        'addr_street': 'addr_street',
                        'addr_zipcode': 'addr_zipcode',
                        'addr_location': 'addr_location',
                        'phone': 'phone',
                        'confirmed': True,
                        }
        self.member = Member.objects.create(**member_data)
        self.member2 = Member.objects.create(**member_data2)
        self.member.user.set_password('12345')
        self.member2.user.set_password('12345')
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_depot_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_subscriptions'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_operations_group'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_send_mails'))
        self.member.user.save()
        self.member2.user.save()
        """
        admin member
        """
        admin_data = {'first_name': 'admin',
                      'last_name': 'last_name',
                      'email': 'admin@email.org',
                      'addr_street': 'addr_street',
                      'addr_zipcode': 'addr_zipcode',
                      'addr_location': 'addr_location',
                      'phone': 'phone',
                      'confirmed': True,
                      }
        self.admin = Member.objects.create(**admin_data)
        self.admin.user.set_password("123456")
        self.admin.user.is_staff = True
        self.admin.user.is_superuser = True
        self.admin.user.save()

    def set_up_shares(self):
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

    def set_up_job(self):
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
        one time jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        one_time_job_data = {'name': 'name',
                             'activityarea': self.area,
                             'duration': 2,
                             'slots': 1,
                             'time': time}
        self.one_time_job1 = OneTimeJob.objects.create(**one_time_job_data)
        """
        assignment
        """
        assignment_data = {'job': self.job2,
                           'member': self.member,
                           'amount': 1}
        Assignment.objects.create(**assignment_data)

    def set_up_sub(self):
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
        sub_data2 = {'depot': self.depot,
                     'future_depot': None,
                     'active': False,
                     'activation_date': None,
                     'deactivation_date': None,
                     'creation_date': '2017-03-27',
                     'start_date': '2018-01-01',
                     'primary_member': self.member2
                     }
        self.sub = Subscription.objects.create(**sub_data)
        self.sub2 = Subscription.objects.create(**sub_data2)
        self.member.subscription = self.sub
        self.member.save()
        self.member2.future_subscription = self.sub2
        self.member2.save()
        TSST.objects.create(subscription=self.sub, type=self.sub_type)
        TFSST.objects.create(subscription=self.sub, type=self.sub_type)

    def assertGet(self, url, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)

    def assertPost(self, url, data=None, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
