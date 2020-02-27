from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from test.util.test import JuntagricoTestCase


class DepotlistTests(JuntagricoTestCase):

    def test_depot_list(self):
        out = StringIO()
        print(timezone.now().timestamp())
        call_command('generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')
        print(timezone.now().timestamp())
