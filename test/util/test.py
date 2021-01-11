from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.utils import timezone

from juntagrico.entity.depot import Depot
from juntagrico.entity.extrasubs import ExtraSubscriptionCategory, ExtraSubscriptionType, ExtraSubscription
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob, Assignment, OneTimeJob, JobExtraType, JobExtra
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JuntagricoTestCase(TestCase):

    def setUp(self):
        self.set_up_member()
        self.set_up_admin()
        self.set_up_shares()
        self.set_up_area()
        self.set_up_job()
        self.set_up_depots()
        self.set_up_sub_types()
        self.set_up_sub()
        self.set_up_extra_sub()
        self.set_up_mail_template()

    @staticmethod
    def create_member(email):
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': email,
                       'addr_street': 'addr_street',
                       'addr_zipcode': 'addr_zipcode',
                       'addr_location': 'addr_location',
                       'phone': 'phone',
                       'mobile_phone': 'phone',
                       'confirmed': True,
                       }
        member = Member.objects.create(**member_data)
        member.user.set_password('12345')
        member.user.save()
        return member

    def set_up_member(self):
        """
            member
        """
        self.member = self.create_member('email1@email.org')
        self.member2 = self.create_member('email2@email.org')
        self.member3 = self.create_member('email3@email.org')
        self.member4 = self.create_member('email4@email.org')
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_depot_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_area_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_members'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_subscriptions'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_operations_group'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_send_mails'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_load_templates'))
        self.member.user.save()

    def set_up_admin(self):
        """
        admin members
        """
        self.admin = self.create_member('admin@email.org')
        self.admin.user.set_password("123456")
        self.admin.user.is_staff = True
        self.admin.user.is_superuser = True
        self.admin.user.save()
        self.area_admin = self.create_member('areaadmin@email.org')
        self.area_admin.user.set_password("123456")
        self.area_admin.user.is_staff = True
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='is_area_admin'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_activityarea'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_assignment'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_jobtype'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_recuringjob'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_onetimejob'))
        self.area_admin.user.save()

    def get_share_data(self, member):
        return {'member': member,
                'paid_date': '2017-03-27',
                'issue_date': '2017-03-27',
                'booking_date': None,
                'cancelled_date': None,
                'termination_date': None,
                'payback_date': None,
                'number': None,
                'notes': ''
                }

    def set_up_shares(self):
        """
        shares
        """
        self.share_data = self.get_share_data(self.member)
        self.share = Share.objects.create(**self.share_data)
        self.share_data4 = self.get_share_data(self.member4)
        self.share4 = Share.objects.create(**self.share_data4)

    def set_up_area(self):
        """
        area
        """
        area_data = {'name': 'name',
                     'coordinator': self.area_admin}
        area_data2 = {'name': 'name2',
                      'coordinator': self.area_admin,
                      'hidden': True}
        self.area = ActivityArea.objects.create(**area_data)
        self.area2 = ActivityArea.objects.create(**area_data2)
        self.member.areas.add(self.area)
        self.member.save()

    def set_up_job(self):
        """
        job_type
        """
        job_type_data = {'name': 'nameot',
                         'activityarea': self.area,
                         'default_duration': 2}
        self.job_type = JobType.objects.create(**job_type_data)
        """
        job_extra
        """
        job_extra_type_data = {'name': 'jet',
                               'display_empty': 'empty',
                               'display_full': 'full'}
        self.job_extra_type = JobExtraType.objects.create(**job_extra_type_data)
        job_extra_data = {'recuring_type': self.job_type,
                          'extra_type': self.job_extra_type}
        self.job_extra = JobExtra.objects.create(**job_extra_data)
        """
        jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        job_data = {'slots': 1,
                    'time': time,
                    'type': self.job_type}
        job_data2 = {'slots': 6,
                     'time': time,
                     'type': self.job_type}
        self.job1 = RecuringJob.objects.create(**job_data)
        self.job2 = RecuringJob.objects.create(**job_data)
        self.job3 = RecuringJob.objects.create(**job_data)
        self.job4 = RecuringJob.objects.create(**job_data2)
        self.job5 = RecuringJob.objects.create(**job_data)
        """
        one time jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        one_time_job_data = {'name': 'name',
                             'activityarea': self.area,
                             'default_duration': 2,
                             'slots': 1,
                             'time': time}
        self.one_time_job1 = OneTimeJob.objects.create(**one_time_job_data)
        """
        assignment
        """
        assignment_data = {'job': self.job2,
                           'member': self.member,
                           'amount': 1}
        self.assignment = Assignment.objects.create(**assignment_data)

    def set_up_depots(self):
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

    def set_up_sub_types(self):
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

    def set_up_sub(self):
        """
        subscription
        """
        sub_data = {'depot': self.depot,
                    'future_depot': None,
                    'activation_date': timezone.now().date(),
                    'deactivation_date': None,
                    'creation_date': '2017-03-27',
                    'start_date': '2018-01-01',
                    }
        sub_data2 = {'depot': self.depot,
                     'future_depot': None,
                     'activation_date': None,
                     'deactivation_date': None,
                     'creation_date': '2017-03-27',
                     'start_date': '2018-01-01'
                     }
        self.sub = Subscription.objects.create(**sub_data)
        self.sub2 = Subscription.objects.create(**sub_data2)
        self.member.join_subscription(self.sub)
        self.sub.primary_member = self.member
        self.sub.save()
        self.member3.join_subscription(self.sub)
        self.member2.join_subscription(self.sub2)
        self.sub2.primary_member = self.member2
        self.sub2.save()
        SubscriptionPart.objects.create(subscription=self.sub, type=self.sub_type)

    def set_up_extra_sub(self):
        '''
        extra subscription
        '''
        esub_cat_data = {'name': 'Extrasub_Category'}
        self.esub_cat = ExtraSubscriptionCategory.objects.create(**esub_cat_data)
        esub_type_data = {'name': 'Extrasub_Type',
                          'description': 'desc',
                          'category': self.esub_cat}
        self.esub_type = ExtraSubscriptionType.objects.create(**esub_type_data)
        esub_data = {'main_subscription': self.sub2,
                     'type': self.esub_type}
        self.esub = ExtraSubscription.objects.create(**esub_data)
        self.esub2 = ExtraSubscription.objects.create(**esub_data)

    def set_up_mail_template(self):
        mail_template_data = {'name': 'MailTemplate'}
        self.mail_template = MailTemplate.objects.create(**mail_template_data)

    def assertGet(self, url, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=200, member=None):
        login_member = member or self.member
        self.client.force_login(login_member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
        return response
