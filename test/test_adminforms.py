import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

from juntagrico.admins.forms.job_copy_form import JobCopyForm
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.share import Share
from juntagrico.admins.forms.admin_mark_share import MarkShareOptionsForm
from test.util.test import JuntagricoTestCase


class AdminTests(JuntagricoTestCase):

    def testCopyJobForm(self):
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '26.07.2020',
                'end_date': '26.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError):
            form.clean()
        self.job1.time = datetime.datetime.now()
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        form.clean()
        form.save_m2m()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '15.07.2020',
                'weekly': '14'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 2)

    def testSubscriptionAdminForm(self):
        def state_part(p_sub, p_data, p_member, p_primary=False, p_save=False):
            SubscriptionAdminForm(instance=p_sub)
            i_form = SubscriptionAdminForm(instance=p_sub, data=p_data)
            i_form.full_clean()
            i_form.clean()
            i_form.save_m2m()
            p_data['subscription_members'].append(p_member)
            i_form = SubscriptionAdminForm(instance=p_sub, data=p_data)
            i_form.full_clean()
            i_form.save_m2m()
            p_data['subscription_members'].remove(p_member)
            if p_primary:
                data['primary_member'] = member
            i_form = SubscriptionAdminForm(instance=p_sub, data=p_data)
            i_form.full_clean()
            i_form.save_m2m()
            if p_save:
                i_form.save()
        # empty
        SubscriptionAdminForm()
        # waiting
        form = SubscriptionAdminForm(instance=self.sub2)
        data = form.initial
        data['subscription_members'] = list(self.sub2.recipients)
        member = self.create_member('toadd@email.org')
        state_part(self.sub2, data, member)
        # inactive
        now = timezone.now().date()
        self.sub2.activation_date = now
        self.sub2.cancellation_date = now
        self.sub2.deactivation_date = now
        self.sub2.primary_member.old_subscriptions.add(self.sub2)
        self.sub2.primary_member.save()
        data['activation_date'] = now
        data['cancellation_date'] = now
        data['deactivation_date'] = now
        state_part(self.sub2, data, member)
        # active
        form = SubscriptionAdminForm(instance=self.sub)
        data = form.initial
        data['activation_date'] = now
        data['subscription_members'] = list(self.sub.recipients)
        state_part(self.sub, data, member, True, True)

    def testShareActionMarkAs(self):
        """
        Testing mark_as action
        App is juntagrico, model is Share
        """
        change_url = reverse("admin:juntagrico_share_changelist")
        shares = [Share.objects.create(member_id=self.member.id),
                  Share.objects.create(member_id=self.member.id)]
        share_pks = [share.pk for share in shares]
        test_fields = ['paid_date', 'issue_date', 'booking_date',
                       'cancelled_date', 'termination_date', 'payback_date']
        data = {'action': 'mark_share',
                '_selected_action': share_pks}
        self.client.force_login(self.admin.user)
        response = self.client.post(change_url, data)
        self.assertEqual(response.status_code, 200)

        now = timezone.now().date()
        form_data = {'target_field': 'paid_date',
                     'date': now,
                     'overwrite': False}
        form = MarkShareOptionsForm(form_data)
        self.assertTrue(form.is_valid())

        for field in test_fields:
            data = {'action': 'mark_share',
                    '_selected_action': share_pks,
                    'apply': True,
                    'target_field': field,
                    'date': now,
                    'overwrite': True}
            response = self.client.post(change_url, data, follow=True)
            self.assertEqual(response.status_code, 200)
            for share in shares:
                share.refresh_from_db()
                self.assertEqual(getattr(share, field), now)
