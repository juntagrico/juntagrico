from io import StringIO

from django.core.management import call_command

from test.util.test import JuntagricoTestCase


class TestdataTests(JuntagricoTestCase):

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
