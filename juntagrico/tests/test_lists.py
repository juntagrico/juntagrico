from io import StringIO

from django.core.files.storage import default_storage
from django.template.loader import get_template
from django.test import override_settings
from django.urls import reverse
from django.core.management import call_command

from ..util.depot_list import depot_list_data
from . import JuntagricoTestCase


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
})
class DepotlistGenerationTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.sub2.activate()
        cls.sub.primary_member = cls.member3
        cls.sub.save()
        cls.sub4 = cls.create_sub_now(cls.depot, future_depot=cls.depot2)
        cls.member4.join_subscription(cls.sub4, True)

    def tearDown(self):
        default_storage.delete('depotlist.pdf')
        default_storage.delete('depot_overview.pdf')
        default_storage.delete('amount_overview.pdf')

    def assertListsCreated(self):
        self.assertTrue(default_storage.exists('depotlist.pdf'))
        self.assertTrue(default_storage.exists('depot_overview.pdf'))
        self.assertTrue(default_storage.exists('amount_overview.pdf'))

    def testDepotListData(self):
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

    def testManualDepotListGeneration(self):
        url = reverse('lists')
        data = {
            'for_date': '2025-12-31',
            'future': False,
            'submit': 'yes',
        }
        # member has no access
        self.assertPost(url, data, code=200)
        self.assertFalse(default_storage.exists('depotlist.pdf'))
        # admin has access
        self.assertPost(url, data, code=302, member=self.admin)
        self.assertListsCreated()
        self.sub4.refresh_from_db()
        self.assertEqual(self.sub4.depot, self.depot)

    def testManualDepotListGenerationWithDepotChange(self):
        url = reverse('lists')
        data = {
            'for_date': '2025-12-31',
            'future': True,
            'submit': 'yes',
        }
        self.assertPost(url, data, code=302, member=self.admin)
        self.assertListsCreated()
        self.sub4.refresh_from_db()
        self.assertEqual(self.sub4.depot, self.depot2)

    def testGenerateDepotListCommand(self):
        out = StringIO()
        call_command('generate_depot_list', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')
        self.assertListsCreated()


class DepotListTests(JuntagricoTestCase):
    def testViewDepotList(self):
        url = reverse('lists')
        self.assertGet(url)
        self.assertGet(url, member=self.member2, code=302)

    def testDownloadDepotList(self):
        for depot_list in ['depotlist', 'depot_overview', 'amount_overview']:
            url = reverse('lists-download', args=[depot_list])
            self.assertGet(url)
            self.assertGet(url, member=self.member2, code=302)

    def testUndefinedDepotListDownloadFails(self):
        url = reverse('lists-download', args=['undefined_list'])
        self.assertGet(url, code=404)
        self.assertGet(url, member=self.member2, code=302)
