from io import StringIO

from django.core.management import call_command
from django.template.loader import get_template

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
        self.assertListEqual(list(data['subscriptions']), [self.sub2, self.sub, self.sub4, self.canceled_sub])
        # test depot list numbers
        rendered_html = get_template('exports/depotlist.html').render(data)
        self.assertInHTML("""
            <td class="namecol top-border left-border horz-left">first_name2 last_name2</td>
            <td class="top-border left-border">3</td>
        """, rendered_html)
        self.assertInHTML("""
            <td class="namecol top-border left-border horz-left">first_name3 last_name3, first_name1 last_name1</td>
            <td class="top-border left-border">1</td>
        """, rendered_html)
        self.assertInHTML("""
            <td class="namecol top-border left-border horz-left">First_name4 Last_name4</td>
            <td class="top-border left-border">1</td>
        """, rendered_html)
        self.assertInHTML("""
            <td class="namecol top-border left-border horz-left">first_name6 last_name6</td>
            <td class="top-border left-border">1</td>
        """, rendered_html)
        # test depot overview
        rendered_html = get_template('exports/depot_overview.html').render(data)
        self.assertInHTML("""
            <td style="width:360px;">depot</td>
            <td style="text-align:right">6</td>
        """, rendered_html)
        self.assertInHTML("""
            <td style="width:360px;">depot2</td>
            <td style="text-align:right">0</td>
        """, rendered_html)
        self.assertInHTML("""
            <td>Total</td>
            <td style="text-align:right">6</td>
        """, rendered_html)
        # test amound overview numbers
        rendered_html = get_template('exports/amount_overview.html').render(data)
        self.assertInHTML("""
            <tr>
                <td class="small bottom-border left-border right-border">Ausfahrt</td>
                <td class="small bottom-border  right-border">Total</td>
                <td class="small bottom-border left-border">product size (1)</td>
            </tr>
            <tr>
                <td>Tour1</td>
                <td style="text-align:right">6</td>
                <td style="text-align:right">6</td>
            </tr>
            <tr>
                <td><b>Alle</b></td>
                <td style="text-align:right">6</td>
                <td style="text-align:right">6</td>
            </tr>
        """, rendered_html)
