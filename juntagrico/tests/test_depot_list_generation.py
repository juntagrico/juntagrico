from io import StringIO

from django.core.management import call_command

from . import JuntagricoTestCase
from ..util.depot_list import depot_list_data


class DepotlistTests(JuntagricoTestCase):
    def test_depot_list(self):
        out = StringIO()
        call_command('generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_depot_list_data(self):
        self.sub2.activate()
        self.sub.primary_member = self.member3
        self.sub.save()
        data = depot_list_data()
        self.assertEqual(data['subscriptions'].first(), self.sub2)
        self.assertEqual(data['subscriptions'].last(), self.sub)
