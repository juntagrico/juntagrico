from io import StringIO

from django.core.management import call_command

from test.util.test import JuntagricoTestCase


class TestdataTests(JuntagricoTestCase):

    def test_generate_testdata(self):
        out = StringIO()
        call_command('generate_testdata', stdout=out)
        self.assertEqual(out.getvalue(), '')
