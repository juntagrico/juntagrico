import datetime

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from juntagrico.entity.delivery import Delivery, DeliveryItem
from juntagrico.entity.depot import Depot, Tour, DepotSubscriptionTypeCondition
from juntagrico.entity.jobs import ActivityArea, JobType, RecuringJob, Assignment, OneTimeJob, JobExtraType, JobExtra
from juntagrico.entity.location import Location
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JuntagricoTestCase(TestCase):
    fixtures = ['test/members', 'test/areas']

    _count_sub_types = 0

    @classmethod
    def setUpTestData(cls):
        # load from fixtures
        cls.load_members()
        cls.load_areas()
        # setup other objects
        cls.set_up_job()
        cls.set_up_depots()
        cls.set_up_sub_types()
        cls.set_up_sub()
        cls.set_up_extra_sub_types()
        cls.set_up_extra_sub()
        cls.set_up_mail_template()
        cls.set_up_deliveries()
        # Use this command here to create fixtures fast:
        # from django.core.management import call_command
        # call_command('dumpdata', 'juntagrico.{model to export}', '-o', 'juntagrico/fixtures/test/data.json',
        #              '--indent', '4', '--natural-primary', '--natural-foreign')

    @classmethod
    def load_members(cls):
        cls.member, cls.member2, cls.member3, cls.member4, cls.member5, cls.member6 = Member.objects.order_by('id')[:6]
        cls.admin = Member.objects.get(email='admin@email.org')

    @classmethod
    def load_areas(cls):
        cls.area_admin = Member.objects.get(email='areaadmin@email.org')
        cls.area, cls.area2 = ActivityArea.objects.order_by('id')[:2]

    @staticmethod
    def create_member(email, **kwargs):
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
        member_data.update(kwargs)
        return Member.objects.create(**member_data)

    @staticmethod
    def create_paid_share(member, **kwargs):
        if settings.ENABLE_SHARES:
            return Share.objects.create(
                member=member,
                paid_date='2017-03-27',
                issue_date='2017-03-27',
                **kwargs
            )

    @classmethod
    def create_paid_and_canceled_share(cls, member, **kwargs):
        return cls.create_paid_share(
            member=member,
            booking_date='2017-12-27',
            cancelled_date='2017-12-27',
            termination_date='2017-12-27',
            **kwargs
        )

    @staticmethod
    def create_location(name='location1', **kwargs):
        location_data = {'name': name,
                         'latitude': '12.513',
                         'longitude': '1.314',
                         'addr_street': 'Fakestreet 123',
                         'addr_zipcode': '1000',
                         'addr_location': 'Faketown',
                         'description': 'Place to be'}
        location_data.update(kwargs)
        return Location.objects.create(**location_data)

    @classmethod
    def set_up_job(cls):
        """
        job_type
        """
        job_type_data = {'name': 'nameot',
                         'activityarea': cls.area,
                         'default_duration': 2,
                         'location': cls.create_location('area_location1')}
        cls.job_type = JobType.objects.create(**job_type_data)
        job_type_data2 = {'name': 'nameot2',
                          'activityarea': cls.area2,
                          'default_duration': 4,
                          'location': cls.create_location('area_location2')}
        cls.job_type2 = JobType.objects.create(**job_type_data2)
        """
        job_extra
        """
        job_extra_type_data = {'name': 'jet',
                               'display_empty': 'empty',
                               'display_full': 'full'}
        cls.job_extra_type = JobExtraType.objects.create(**job_extra_type_data)
        job_extra_data = {'recuring_type': cls.job_type,
                          'extra_type': cls.job_extra_type}
        cls.job_extra = JobExtra.objects.create(**job_extra_data)
        """
        jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        job_data = {'slots': 1,
                    'time': time,
                    'type': cls.job_type}
        job_data2 = {'slots': 6,
                     'time': time,
                     'type': cls.job_type}
        job_data3 = {'slots': 5,
                     'time': time,
                     'type': cls.job_type}
        cls.job1 = RecuringJob.objects.create(**job_data)
        cls.job2 = RecuringJob.objects.create(**job_data)
        cls.job3 = RecuringJob.objects.create(**job_data)
        cls.job4 = RecuringJob.objects.create(**job_data2)
        cls.job5 = RecuringJob.objects.create(**job_data)
        cls.job6 = RecuringJob.objects.create(**job_data3)
        cls.past_job = RecuringJob.objects.create(
            slots=2,
            time=timezone.now() - timezone.timedelta(hours=2),
            type=cls.job_type
        )
        cls.past_core_job = RecuringJob.objects.create(
            slots=2,
            time=timezone.now() - timezone.timedelta(hours=2),
            type=cls.job_type2
        )
        cls.infinite_job = RecuringJob.objects.create(**{
            'infinite_slots': True,
            'time': time,
            'type': cls.job_type
        })
        """
        one time jobs
        """
        time = timezone.now() + timezone.timedelta(hours=2)
        one_time_job_data = {'name': 'name',
                             'activityarea': cls.area,
                             'default_duration': 2,
                             'slots': 1,
                             'time': time,
                             'location': cls.create_location('job_location1')}
        cls.one_time_job1 = OneTimeJob.objects.create(**one_time_job_data)
        one_time_job_data.update(name='name2', time=timezone.now() - timezone.timedelta(hours=2))
        cls.past_one_time_job = OneTimeJob.objects.create(**one_time_job_data)
        """
        assignment
        """
        cls.assignment = cls.create_assignment(cls.job2, cls.member)
        # needed to test assignment widget fully
        cls.create_assignment(cls.past_job, cls.member)
        cls.create_assignment(cls.past_core_job, cls.member)
        cls.create_assignment(cls.past_job, cls.member3)
        cls.create_assignment(cls.past_core_job, cls.member3)

    @staticmethod
    def create_assignment(job, member, amount=1, **kwargs):
        return Assignment.objects.create(job=job, member=member, amount=amount, **kwargs)

    @classmethod
    def set_up_depots(cls):
        """
        depots
        """
        cls.tour = Tour.objects.create(name='Tour1', description='Tour1 description')
        location = cls.create_location('depot_location')
        depot_data = {
            'name': 'depot',
            'contact': cls.member,
            'tour': cls.tour,
            'weekday': 1,
            'location': location,
        }
        cls.depot = Depot.objects.create(**depot_data)
        depot_data = {
            'name': 'depot2',
            'contact': cls.member,
            'weekday': 1,
            'pickup_time': datetime.time(9, 0),
            'pickup_duration': 48,
            'tour': cls.tour,
            'location': location,
            'fee': 55.0,
        }
        cls.depot2 = Depot.objects.create(**depot_data)

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

    @classmethod
    def set_up_sub_types(cls):
        """
        subscription product, size and types
        """
        sub_product_data = {
            'name': 'product'
        }
        cls.sub_product = SubscriptionProduct.objects.create(**sub_product_data)
        sub_size_data = {
            'name': 'sub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': cls.sub_product,
            'description': 'sub_desc'
        }
        cls.sub_size = SubscriptionSize.objects.create(**sub_size_data)
        cls.sub_type = cls.create_sub_type(cls.sub_size)
        cls.sub_type2 = cls.create_sub_type(cls.sub_size, shares=2)
        cls.sub_type3 = cls.create_sub_type(cls.sub_size, shares=0)
        DepotSubscriptionTypeCondition.objects.create(
            depot=cls.depot,
            subscription_type=cls.sub_type,
            fee=100
        )
        DepotSubscriptionTypeCondition.objects.create(
            depot=cls.depot2,
            subscription_type=cls.sub_type2,
            fee=50
        )

    @staticmethod
    def create_sub(depot, parts, activation_date=None, **kwargs):
        if 'deactivation_date' in kwargs and 'cancellation_date' not in kwargs:
            kwargs['cancellation_date'] = activation_date
        sub = Subscription.objects.create(
            depot=depot,
            activation_date=activation_date,
            creation_date='2017-03-27',
            start_date='2018-01-01',
            **kwargs
        )
        if isinstance(parts, SubscriptionType):
            parts = [parts]
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
    def create_sub_now(cls, depot, parts=None, **kwargs):
        if not parts:
            parts = [cls.sub_type]
        return cls.create_sub(depot, parts, datetime.date.today(), **kwargs)

    @classmethod
    def set_up_sub(cls):
        """
        subscription
        """
        today = datetime.date.today()
        # sub 3 (inactive)
        cls.sub3 = cls.create_sub(cls.depot, cls.sub_type3)
        cls.member3.join_subscription(cls.sub3, True)
        cls.sub3.activate(today - datetime.timedelta(3))
        cls.sub3.deactivate(today - datetime.timedelta(1))
        # sub (active, 2 members)
        cls.sub = cls.create_sub_now(cls.depot)
        cls.member.join_subscription(cls.sub, True)
        cls.member3.join_subscription(cls.sub)
        # sub2 (waiting)
        cls.sub2 = cls.create_sub(cls.depot, cls.sub_type2)
        cls.member2.join_subscription(cls.sub2, True)
        # cancelled_sub
        cls.cancelled_sub = cls.create_sub_now(cls.depot, cancellation_date=today)
        cls.member6.join_subscription(cls.cancelled_sub, True)

    @classmethod
    def set_up_extra_sub_types(cls):
        """
        subscription product, size and types
        """
        extrasub_product_data = {
            'name': 'extraproduct',
            'is_extra': True
        }
        cls.extrasub_product = SubscriptionProduct.objects.create(**extrasub_product_data)
        extrasub_size_data = {
            'name': 'extrasub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': cls.extrasub_product,
            'description': 'sub_desc'
        }
        cls.extrasub_size = SubscriptionSize.objects.create(**extrasub_size_data)
        extrasub_type_data = {
            'name': 'extrasub_type_name',
            'long_name': 'sub_type_long_name',
            'size': cls.extrasub_size,
            'shares': 0,
            'visible': True,
            'required_assignments': 10,
            'price': 1000,
            'description': 'sub_type_desc'}
        cls.extrasub_type = SubscriptionType.objects.create(**extrasub_type_data)

    @classmethod
    def set_up_extra_sub(cls):
        '''
        extra subscription
        '''
        esub_data = {'subscription': cls.sub2,
                     'type': cls.extrasub_type}
        cls.esub = SubscriptionPart.objects.create(**esub_data)
        cls.esub2 = SubscriptionPart.objects.create(**esub_data)

    @classmethod
    def set_up_mail_template(cls):
        mail_template_data = {'name': 'MailTemplate'}
        cls.mail_template = MailTemplate.objects.create(**mail_template_data)

    @classmethod
    def set_up_deliveries(cls):
        delivery_data = {'delivery_date': '2017-03-27',
                         'tour': cls.tour,
                         'subscription_size': cls.sub_size}
        cls.delivery1 = Delivery.objects.create(**delivery_data)
        delivery_data['delivery_date'] = '2017-03-28'
        cls.delivery2 = Delivery.objects.create(**delivery_data)
        DeliveryItem.objects.create(delivery=cls.delivery1)

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


class JuntagricoTestCaseWithShares(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + (['test/shares'] if settings.ENABLE_SHARES else [])
