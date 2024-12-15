from io import StringIO

from django.core.management import call_command

from . import JuntagricoTestCase
from ..util.depot_list import depot_list_data


class DepotlistTests(JuntagricoTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sub2.activate()
        cls.sub.primary_member = cls.member3
        cls.sub.save()
        cls.sub4 = cls.create_sub_now(cls.depot)
        cls.member4.join_subscription(cls.sub4, True)

    def test_depot_list(self):
        out = StringIO()
        call_command('generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')

    def test_depot_list_data(self):
        data = depot_list_data()
        self.assertListEqual(list(data['subscriptions']), [self.sub2, self.sub, self.sub4, self.cancelled_sub])
