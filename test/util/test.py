from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail

from juntagrico.entity.delivery import Delivery, DeliveryItem
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob, Assignment, OneTimeJob, JobExtraType, JobExtra
from juntagrico.entity.location import Location
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JuntagricoTestCase(TestCase):

    _count_sub_types = 0

    def setUp(self):
        self.set_up_member()
        self.set_up_admin()
        self.set_up_shares()
        self.set_up_area()
        self.set_up_location()
        self.set_up_job()
        self.set_up_depots()
        self.set_up_sub_types()
        self.set_up_sub()
        self.set_up_extra_sub_types()
        self.set_up_extra_sub()
        self.set_up_mail_template()
        self.set_up_deliveries()
        mail.outbox.clear()

    @staticmethod
    def create_member(email):
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': email,
                       'addr_street': 'addr_street',
                       'addr_zipcode': '1234',
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
        self.member5 = self.create_member('email5@email.org')
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_depot_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_area_admin'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_members'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_filter_subscriptions'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_subscription'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_member'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_share'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_assignment'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_subscriptionpart'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_view_lists'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_view_exports'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='is_operations_group'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_send_mails'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='can_load_templates'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='change_subscriptionpart'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_subscription_creation'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_member_creation'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_share_creation'))
        self.member.user.save()

    def set_up_superuser(self):
        """
        superuser with member (admin)
        """
        self.admin = self.create_member('admin@email.org')
        self.admin.user.set_password("123456")
        self.admin.user.is_staff = True
        self.admin.user.is_superuser = True
        self.admin.user.save()

    def set_up_admin(self):
        """
        admin members
        """
        self.set_up_superuser()
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
            Permission.objects.get(codename='add_recuringjob'))
        self.area_admin.user.user_permissions.add(
            Permission.objects.get(codename='change_onetimejob'))
        self.area_admin.user.save()

    @staticmethod
    def create_paid_share(member, **kwargs):
        return Share.objects.create(
            member=member,
            paid_date='2017-03-27',
            issue_date='2017-03-27',
            **kwargs
        )

    @classmethod
    def create_paid_and_cancelled_share(cls, member, **kwargs):
        return cls.create_paid_share(
            member=member,
            booking_date='2017-12-27',
            cancelled_date='2017-12-27',
            termination_date='2017-12-27',
            **kwargs
        )

    def set_up_shares(self):
        """
        shares
        """
        self.share = self.create_paid_share(self.member)
        self.share4 = self.create_paid_share(self.member4)
        self.share5 = self.create_paid_and_cancelled_share(self.member5)

    def set_up_area(self):
        """
        area
        """
        area_data = {'name': 'name',
                     'coordinator': self.area_admin,
                     'auto_add_new_members': True}
        area_data2 = {'name': 'name2',
                      'coordinator': self.area_admin,
                      'hidden': True}
        self.area = ActivityArea.objects.create(**area_data)
        self.area2 = ActivityArea.objects.create(**area_data2)
        self.member.areas.add(self.area)
        self.member.save()

    def set_up_location(self):
        """
        location
        """
        location_data = {'name': 'location1',
                         'latitude': '12.513',
                         'longitude': '1.314',
                         'addr_street': 'Fakestreet 123',
                         'addr_zipcode': '1000',
                         'addr_location': 'Faketown',
                         'description': 'Place to be'}
        location_data2 = {'name': 'location2'}
        self.location = Location.objects.create(**location_data)
        self.location2 = Location.objects.create(**location_data2)
        location_data_depot = {'name': 'Depot location',
                               'latitude': '12.513',
                               'longitude': '1.314',
                               'addr_street': 'Fakestreet 123',
                               'addr_zipcode': '1000',
                               'addr_location': 'Faketown',
                               'description': 'Place to be'}
        self.location_depot = Location.objects.create(**location_data_depot)

    def set_up_job(self):
        """
        job_type
        """
        job_type_data = {'name': 'nameot',
                         'activityarea': self.area,
                         'default_duration': 2,
                         'location': self.location}
        self.job_type = JobType.objects.create(**job_type_data)
        job_type_data2 = {'name': 'nameot2',
                          'activityarea': self.area2,
                          'default_duration': 4,
                          'location': self.location2}
        self.job_type2 = JobType.objects.create(**job_type_data2)
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
        job_data3 = {'slots': 5,
                     'time': time,
                     'type': self.job_type,
                     'allow_unsubscribe': True}
        self.job1 = RecuringJob.objects.create(**job_data)
        self.job2 = RecuringJob.objects.create(**job_data)
        self.job3 = RecuringJob.objects.create(**job_data)
        self.job4 = RecuringJob.objects.create(**job_data2)
        self.job5 = RecuringJob.objects.create(**job_data)
        self.job6 = RecuringJob.objects.create(**job_data3)
        self.past_job = RecuringJob.objects.create(
            slots=1,
            time=timezone.now() - timezone.timedelta(hours=2),
            type=self.job_type
        )
        self.infinite_job = RecuringJob.objects.create(**{
            'infinite_slots': True,
            'time': time,
            'type': self.job_type
        })
        """
        one time jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        one_time_job_data = {'name': 'name',
                             'activityarea': self.area,
                             'default_duration': 2,
                             'slots': 1,
                             'time': time,
                             'location': self.location2}
        self.one_time_job1 = OneTimeJob.objects.create(**one_time_job_data)
        one_time_job_data.update(name='name2', time=timezone.now() - timezone.timedelta(hours=2))
        self.past_one_time_job = OneTimeJob.objects.create(**one_time_job_data)
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
            'name': 'depot',
            'contact': self.member,
            'weekday': 1,
            'location': self.location_depot}
        self.depot = Depot.objects.create(**depot_data)
        depot_data = {
            'name': 'depot2',
            'contact': self.member,
            'weekday': 1,
            'location': self.location_depot}
        self.depot2 = Depot.objects.create(**depot_data)

    @staticmethod
    def create_sub_type(size, shares=1, visible=True, required_assignments=10, required_core_assignments=3, price=1000, **kwargs):
        JuntagricoTestCase._count_sub_types += 1
        name = kwargs.get('name', None)
        long_name = kwargs.get('long_name', 'sub_type_long_name')
        return SubscriptionType.objects.create(
            name=name or 'sub_type_name' + str(JuntagricoTestCase._count_sub_types),
            long_name=long_name,
            size=size,
            shares=shares,
            visible=visible,
            required_assignments=required_assignments,
            required_core_assignments=required_core_assignments,
            price=price,
            **kwargs
        )

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
        self.sub_type = self.create_sub_type(self.sub_size)
        self.sub_type2 = self.create_sub_type(self.sub_size, shares=2)

    @staticmethod
    def create_sub(depot, activation_date=None, parts=None, **kwargs):
        if 'deactivation_date' in kwargs and 'cancellation_date' not in kwargs:
            kwargs['cancellation_date'] = activation_date
        sub = Subscription.objects.create(
            depot=depot,
            activation_date=activation_date,
            creation_date='2017-03-27',
            start_date='2018-01-01',
            **kwargs
        )
        if parts:
            for part in parts:
                SubscriptionPart.objects.create(
                    subscription=sub,
                    type=part,
                    activation_date=activation_date,
                    cancellation_date=kwargs.get('cancellation_date', None),
                    deactivation_date=kwargs.get('deactivation_date', None)
                )
        return sub

    @classmethod
    def create_sub_now(cls, depot, **kwargs):
        return cls.create_sub(depot, timezone.now().date(), **kwargs)

    def set_up_sub(self):
        """
        subscription
        """
        self.sub = self.create_sub_now(self.depot)
        self.sub2 = self.create_sub(self.depot)
        self.member.join_subscription(self.sub, True)
        self.member3.join_subscription(self.sub)
        self.member2.join_subscription(self.sub2, True)
        SubscriptionPart.objects.create(subscription=self.sub, type=self.sub_type, activation_date=timezone.now().date())

    def set_up_extra_sub_types(self):
        """
        subscription product, size and types
        """
        extrasub_product_data = {
            'name': 'extraproduct',
            'is_extra': True
        }
        self.extrasub_product = SubscriptionProduct.objects.create(**extrasub_product_data)
        extrasub_size_data = {
            'name': 'extrasub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': self.extrasub_product,
            'description': 'sub_desc'
        }
        self.extrasub_size = SubscriptionSize.objects.create(**extrasub_size_data)
        extrasub_type_data = {
            'name': 'extrasub_type_name',
            'long_name': 'sub_type_long_name',
            'size': self.extrasub_size,
            'shares': 0,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.extrasub_type = SubscriptionType.objects.create(**extrasub_type_data)

    def set_up_extra_sub(self):
        '''
        extra subscription
        '''
        esub_data = {'subscription': self.sub2,
                     'type': self.extrasub_type}
        self.esub = SubscriptionPart.objects.create(**esub_data)
        self.esub2 = SubscriptionPart.objects.create(**esub_data)

    def set_up_mail_template(self):
        mail_template_data = {'name': 'MailTemplate'}
        self.mail_template = MailTemplate.objects.create(**mail_template_data)

    def set_up_deliveries(self):
        delivery_data = {'delivery_date': '2017-03-27',
                         'subscription_size': self.sub_size}
        self.delivery1 = Delivery.objects.create(**delivery_data)
        delivery_data['delivery_date'] = '2017-03-28'
        self.delivery2 = Delivery.objects.create(**delivery_data)
        DeliveryItem.objects.create(delivery=self.delivery1)

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
