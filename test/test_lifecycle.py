from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from test.util.test import JuntagricoTestCase


class ListTests(JuntagricoTestCase):

    def testSubDeactivation(self):
        now = timezone.now().date()
        start = now - timedelta(days=10)
        end = now - timedelta(days=5)
        member = self.create_member('email@email.email')
        share_data = self.get_share_data(member)
        Share.objects.create(**share_data)
        Share.objects.create(**share_data)
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
        SubscriptionPart.objects.create(subscription=sub, type=self.sub_type, activation_date=start, cancellation_date=now, deactivation_date=now)
        try:
            sub.deactivate(end)
        except ValidationError:
            pass
        sub.refresh_from_db()
        self.assertIsNone(sub.deactivation_date)
        partone.refresh_from_db()
        self.assertIsNone(partone.deactivation_date)
        sub.deactivate(now)
        sub.refresh_from_db()
        self.assertIsNotNone(sub.deactivation_date)
        partone.refresh_from_db()
        self.assertIsNotNone(partone.deactivation_date)
