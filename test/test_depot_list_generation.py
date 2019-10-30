from io import StringIO

from django.core.management import call_command

from test.util.test import JuntagricoTestCase


class DepotlistTests(JuntagricoTestCase):

    def test_depot_list(self):
        out = StringIO()
        call_command('generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')
