from django.conf import settings
from django.urls import reverse

from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.tests import JuntagricoTestCaseWithShares


class SubscriptionTests(JuntagricoTestCaseWithShares):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # ensure there are enough shares
        if settings.ENABLE_SHARES:
            cls.create_paid_share(cls.member)
            cls.create_paid_share(cls.member)

    def testSubChange(self):
        self.assertGet(reverse('sub-change', args=[self.sub.pk]))

    def testSub(self):
        self.assertGet(reverse('subscription-landing'))
        self.assertGet(reverse('subscription-single', args=[self.sub.pk]))

    def testSizeChange(self):
        self.assertGet(reverse('size-change', args=[self.sub.pk]))
        post_data = {
            f'amount[{type_id}]': 1 if i == 1 else 0
            for i, type_id in enumerate(SubscriptionType.objects.order_by('id').values_list('id', flat=True))
        }
        self.assertPost(reverse('size-change', args=[self.sub.pk]), post_data, code=302)
