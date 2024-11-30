from io import StringIO

from django.core import mail
from django.core.management import call_command

from . import JuntagricoTestCaseWithShares


class ManagementCommandsTest(JuntagricoTestCaseWithShares):
    def test_create_member_for_superuser(self):
        call_command('createsuperuser', username='testsuperuer', email='super@mail.com', no_input='')
        out = StringIO()
        call_command('create_member_for_superusers', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_generate_testdata(self):
        out = StringIO()
        call_command('generate_testdata', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_generate_testdata_advanced(self):
        out = StringIO()
        call_command('generate_testdata_advanced', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_mailtexts(self):
        out = StringIO()
        call_command('mailtexts', stderr=out)
        self.assertEqual(out.getvalue(), '')

    def test_remind_members(self):
        # add another assignment of member to job2
        self.create_assignment(self.job2, self.member)
        out = StringIO()
        call_command('remind_members', stderr=out)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(len(mail.outbox), 1)
        # expect only 1 recipient, event when signed up twice
        self.assertListEqual(mail.outbox[0].recipients(), [self.member.email])
