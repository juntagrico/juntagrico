from io import StringIO

from django.core.management import call_command

from test.util.test import JuntagricoTestCase


class ManagementCommandsTest(JuntagricoTestCase):

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