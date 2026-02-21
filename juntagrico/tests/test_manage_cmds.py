from copy import deepcopy
from io import StringIO

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import override_settings, TestCase

from . import JuntagricoTestCaseWithShares
from ..entity.jobs import RecuringJob
from ..entity.member import Member


class ManagementCommandsTest(JuntagricoTestCaseWithShares):
    def test_create_member_for_superuser(self):
        call_command('createsuperuser', username='testsuperuser', email='super@mail.com', no_input='')
        out = StringIO()
        call_command('create_member_for_superusers', stdout=out)
        self.assertEqual(out.getvalue(), 'Created 1 member(s) for superusers.\n')

    def test_createadmin(self):
        username = 'testsuperuser'
        email = 'super@mail.com'
        call_command('createadmin', username=username, email=email, no_input='')
        self.assertEqual(Member.objects.get(user__username=username).email, email)

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


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        raise NameError(f"Undefined variable or unknown value for: '{other}'")


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class FreshMailtextTests(TestCase):
    """ Test mailtexts with fresh database
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Modify settings for test
        template_setting = deepcopy(settings.TEMPLATES)
        template_setting[0]['OPTIONS']['string_if_invalid'] = InvalidTemplateVariable('%s')
        cls.override = override_settings(TEMPLATES=template_setting)
        cls.override.enable()  # Activate the override

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()  # Restore settings
        super().tearDownClass()

    def test_mailtexts(self):
        err = StringIO()
        out = StringIO()
        job_count = RecuringJob.objects.count()
        call_command('mailtexts', stderr=err, stdout=out)
        self.assertEqual(err.getvalue(), '')
        self.assertNotIn('%', out.getvalue(), 'some template values could not be rendered')
        self.assertEqual(job_count, RecuringJob.objects.count(), 'test data was not reverted')
