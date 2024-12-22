import datetime

from django.conf import settings
from django.core.exceptions import ValidationError

from juntagrico.entity.subs import Subscription, SubscriptionPart
from . import JuntagricoTestCase


class LifeCycleTests(JuntagricoTestCase):

    def testSubDeactivation(self):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=10)
        end = today - datetime.timedelta(days=5)
        member = self.create_member('email@email.email')
        if settings.ENABLE_SHARES:
            self.create_paid_share(member)
            self.create_paid_share(member)
        sub_data = {'depot': self.depot,
                    'future_depot': None,
                    'activation_date': start,
                    'deactivation_date': None,
                    'creation_date': '2017-03-27',
                    'start_date': '2018-01-01',
                    }
        sub = Subscription.objects.create(**sub_data)
        member.join_subscription(sub)
        sub.primary_member = member
        sub.save()
        partone = SubscriptionPart.objects.create(subscription=sub, type=self.sub_type, activation_date=start)
        SubscriptionPart.objects.create(subscription=sub, type=self.sub_type, activation_date=start,
                                        cancellation_date=today, deactivation_date=today)
        try:
            sub.deactivate(end)
        except ValidationError:
            pass
        sub.refresh_from_db()
        self.assertIsNone(sub.deactivation_date)
        partone.refresh_from_db()
        self.assertIsNone(partone.deactivation_date)
        sub.deactivate(today)
        sub.refresh_from_db()
        self.assertIsNotNone(sub.deactivation_date)
        partone.refresh_from_db()
        self.assertIsNotNone(partone.deactivation_date)
