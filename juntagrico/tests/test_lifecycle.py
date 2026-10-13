import datetime

from django.conf import settings

from juntagrico.entity.subs import Subscription, SubscriptionPart
from . import JuntagricoTestCase


class LifeCycleTests(JuntagricoTestCase):

    def testSubDeactivation(self, days_ago=0):
        today = datetime.date.today()
        start = today - datetime.timedelta(days=10)
        end = today - datetime.timedelta(days=days_ago)
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
        member.join_subscription(sub, True)
        partone = SubscriptionPart.objects.create(subscription=sub, type=self.sub_type, activation_date=start)
        SubscriptionPart.objects.create(subscription=sub, type=self.sub_type, activation_date=start,
                                        cancellation_date=today, deactivation_date=today)
        sub.deactivate(end)
        # deactivation is today in any case, because primary member joined today.
        sub.refresh_from_db()
        self.assertEqual(sub.deactivation_date, today)
        partone.refresh_from_db()
        self.assertEqual(partone.deactivation_date, today)

    def testSubRetroDeactivation(self):
        self.testSubDeactivation(5)
