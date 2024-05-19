from django.contrib.auth.models import Permission
from django.core import mail
from django.core.management import call_command
from django.urls import reverse

from . import JuntagricoTestCase


class DepotChangeTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.admin.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_depot_change'))
        cls.admin.user.save()

        cls.sub3 = cls.create_sub(cls.depot, future_depot=cls.depot2)
        cls.member4.join_subscription(cls.sub3, True)

    def testDepotChangeWaiting(self):
        """For not yet active subscriptions the depot should change immediately"""
        self.assertPost(reverse('depot-change', args=[self.sub2.pk]), {'depot': self.depot2.pk}, member=self.member2)
        self.sub2.refresh_from_db()
        self.assertEqual(self.sub2.depot, self.depot2)
        self.assertIsNone(self.sub2.future_depot)
        self.assertEqual(len(mail.outbox), 1)  # admin notification email

    def testDepotChange(self):
        """On active subscriptions future depot is changed and waits for confirmation"""
        self.assertGet(reverse('depot-change', args=[self.sub.pk]))
        self.assertPost(reverse('depot-change', args=[self.sub.pk]), {'depot': self.depot2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.depot, self.depot)
        self.assertEqual(self.sub.future_depot, self.depot2)
        self.assertEqual(len(mail.outbox), 1)  # admin notification email

    def testDepotChangesList(self):
        """Test that depot change list opens for admins and not for members"""
        self.assertGet(reverse('manage-sub-depot-changes'))
        self.assertGet(reverse('manage-sub-depot-changes'), member=self.member2, code=302)

    def testDepotChangeConfirm(self):
        """Test that admin can confirm a depot change manually, and normal members can't"""
        self.assertGet(reverse('manage-sub-depot-change-confirm', args=[self.sub3.pk]), member=self.member2, code=302)
        self.sub3.refresh_from_db()
        self.assertEqual(self.sub3.depot, self.depot)
        self.assertGet(reverse('manage-sub-depot-change-confirm', args=[self.sub3.pk]), code=302)
        self.sub3.refresh_from_db()
        self.assertEqual(self.sub3.depot, self.depot2)
        self.assertIsNone(self.sub3.future_depot)
        self.assertEqual(len(mail.outbox), 1)  # member notification of depot change

    def testDepotChangeOnListCreation(self):
        """Test that depot changes, when depot list is generated with --future option"""
        call_command('generate_depot_list', '--force', '--future')
        self.sub3.refresh_from_db()
        self.assertEqual(self.sub3.depot, self.depot2)
        self.assertIsNone(self.sub3.future_depot)
        self.assertEqual(len(mail.outbox), 1)  # member notification of depot change
