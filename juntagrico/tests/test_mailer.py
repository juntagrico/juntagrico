from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.test import override_settings, tag, TestCase
from django.urls import reverse

from . import JuntagricoTestCaseWithShares
from ..util.string import int_array_decompress


def mock_batch_mailer(self, msgs):
    # patch batch mailer to not use threads to make it testable
    for msg in msgs:
        self._send_batches(msg, 1, 0)  # testing with individual "to" emails
        self._send_batches(msg, 2, 0)  # testing in batches of 2
        self._send_batches(msg, 4, 3)  # testing with waiting time
        return 1  # pretend message was sent


class AreaMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-area', args=[self.area.id])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_area': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-area-recipients', args=[self.area.id]), data={
            'to_area': 'on'
        })
        self.assertEqual(b'An 4 Personen senden', response.content)


class AreaCoordinatorMailerTests(AreaMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.area_admin_contact

    def testNoAccess(self):
        # no access to other area
        self.assertGet(reverse('email-to-area', args=[self.area2.id]), 403)
        # no access for area coordinator that can't contact
        self.assertGet(reverse('email-to-area', args=[self.area.id]), 403, member=self.area_admin_viewer)


class JobMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-job', args=[self.job2.id])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_job': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-job-recipients', args=[self.job2.id]), data={
            'to_job': 'on'
        })
        self.assertEqual(b'An 1 Person senden', response.content)


class JobCoordinatorMailerTests(JobMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.area_admin_contact

    def testNoAccess(self):
        # no access to other area jobs
        self.assertGet(reverse('email-to-job', args=[self.past_core_job.id]), 403)
        # no access for area coordinator that can't contact
        self.assertGet(reverse('email-to-job', args=[self.job1.id]), 403, member=self.area_admin_viewer)


class DepotMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-depot', args=[self.depot.id])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_depot': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-depot-recipients', args=[self.depot.id]), data={
            'to_depot': 'on'
        })
        self.assertEqual(b'An 4 Personen senden', response.content)


class DepotCoordinatorMailerTests(DepotMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.depot_coordinator

    def testNoAccess(self):
        # no access to other depots
        self.assertGet(reverse('email-to-depot', args=[self.depot2.id]), 403)


class MemberMailerTests(JuntagricoTestCaseWithShares):
    def _testSending(self, sender, to_member):
        url = reverse('email-to-member', args=[to_member.id])
        self.assertGet(url, member=sender)
        self.assertPost(url, member=sender)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_members': [to_member.id],
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302, member=sender)
        self.assertEqual(len(mail.outbox), 1)

    def testSendingWithPermission(self):
        self._testSending(self.member, self.member2)

    def testSendingByAreaAdmin(self):
        # can contact member in area
        self._testSending(self.area_admin_contact, self.member)
        # can contact members that are contactable in general
        mail.outbox = []
        self._testSending(self.area_admin_contact, self.member6)

    def testSendingByDepotAdmin(self):
        # can contact member in depot
        self._testSending(self.depot_coordinator, self.member3)
        # can contact members that are contactable in general
        mail.outbox = []
        self._testSending(self.depot_coordinator, self.member6)

    def testCantContact(self):
        # can't contact inactive member
        self.assertFalse(self.member.can_contact(self.inactive_member))
        self.assertGet(reverse('email-to-member', args=[self.inactive_member.id]), 403)
        # area admin can't contact members outside of area
        self.assertFalse(self.area_admin_contact.can_contact(self.member2))
        # depot admin can't contact members outside of depot
        self.assertFalse(self.depot_coordinator.can_contact(self.member2))


class MailerTests(JuntagricoTestCaseWithShares):
    def testMailer(self):
        # test access
        self.assertGet(reverse('email-write'))
        self.assertGet(reverse('email-write'), member=self.area_admin_contact)
        self.assertGet(reverse('email-write'), member=self.depot_coordinator)
        # test no access
        self.assertGet(reverse('email-write'), member=self.member2, code=302)

    def testMemberMailer(self):
        data = {'members': '1-5_7-87'}
        self.assertGet(reverse('email-write'), data=data)
        # sending members via post should not process the form
        data = data | {
            'from_email': 'private',
            'to_members': [self.member.id],
            'copy': 'on',
            'subject': 'test',
        }
        self.assertPost(reverse('email-write'), data)
        self.assertEqual(len(mail.outbox), 0)

    def testMemberSelectionDecompress(self):
        self.assertSetEqual(
            set(int_array_decompress(
                '1-2_4-7_12-3_5_9-22_4-5_7-9_31-2_4_6_40-1_3_8_50_3_5-7_9-65_8_70-1_3_5-8_83-8_91-6''_9-100_2-4_6-14'
                '_6_21_4_8_31_3-4_9-49_51-2_4_6-9_61_3-6_74_6-82_8-90_3-4_200-1_4_7_9_12_5_7_9-20_3_30_3-5_40_5_7_9-'
                '51_4_6-7_9-60_4_6_70-6_80_4-5_8-91_300-1_3_5-6_9-11_4_22-3_7_30-1_3_7_9_42_52_4_61_3_6_70-1_3_7-8_9'
                '0-1_3-5_8-9_401_3-5_12_4_6-7_24_9-31_8-9_46_51-2_9_68-9_71-2_6_8_85_8_91_531_41_4_52_60_3-4_8_71_3_'
                '8_84-5_8_92_9_602_5_13_7_9_27-8_31-4_6_42_50_2_8_63_6_8_71_4_6_80_8_94_6_8_700_7-8_13_6_20_2_4-7_30'
                '_2_6_8-9_43_7-8_55_61_3_71_5_7_84-6_90_2-3_5_805-6_13-4_8_21_7-30_2-3_7_41-2_4_6_8_54_6_8-9_61_6_71'
                '-3_9_82_6_91_900_2-4_13-4_8-9_28_30_5_9-40_7_9-50_2-4_7_65_70-1_86_8_90_7_1007_14-5_8_22-3_8_32-3_4'
                '0-4_7-51_4-5_61_6_75_81-2_5_7_90-1_101-2_12-7_9-21_3_5-7_33_6_8_44_7_9_59-61_3-4_9-71_8_80-1_3-6_91'
                '-3_200-1_3-5_10_9_24_6-7_30-3_5_7_9-41_4-7_53-6_61_3_5-6_74_7-8_80_3-7_90-1_3-5_7_300-1_3-6_9_11_5_'
                '8_20_2-3_5_7-8_31-2_4-7_42-3_7-8_50-1_3_5-6_64_7_9-70_2_5-6_8-9_91-4_6-7_403-5_7-8_12-3_5-6_8-9_21-'
                '2_4-5_7-9_32_5_8-9_41-2_9-51_3_6_8-60_3_5-7_70-1_6_80-1_4_90-1_3-7_500_2-3_6_10-2_4_7-8_24_7-33_7_4'
                '2_4-6_8_50_2_4-5_2838-42_4-7_50_2-6_8-60'
            )),
            {180, 116, 1300, 1397, 25, 1126, 459, 965, 1115, 755, 666, 1136, 12, 50, 1082, 230, 1210, 1530, 736, 694, 7,
             288, 1163, 485, 471, 1224, 102, 274, 777, 1101, 354, 4, 264, 15, 148, 724, 121, 272, 1042, 235, 250, 6,
             333, 289, 1032, 190, 1403, 1232, 245, 1369, 412, 220, 1356, 266, 1066, 1450, 700, 103, 29, 19, 76, 88, 311,
             1200, 828, 96, 1343, 469, 1227, 814, 1404, 650, 1044, 1117, 957, 990, 636, 1191, 790, 585, 841, 1253, 813,
             273, 177, 2856, 259, 1149, 1413, 1147, 1531, 1113, 1231, 1463, 726, 1394, 361, 658, 1337, 13, 65, 844, 668,
             140, 1291, 806, 856, 305, 904, 1121, 452, 61, 104, 370, 36, 588, 1323, 204, 1480, 1412, 86, 478, 28, 2860,
             872, 1047, 1353, 1334, 403, 785, 821, 113, 708, 240, 472, 157, 451, 1295, 1085, 1303, 1091, 1287, 1164,
             619, 1416, 439, 404, 491, 1458, 986, 21, 1456, 323, 100, 1090, 997, 761, 290, 578, 1427, 352, 94, 1114,
             429, 725, 405, 1015, 1342, 1554, 2852, 270, 159, 85, 571, 930, 147, 829, 775, 71, 188, 2850, 1301, 146,
             1442, 2853, 544, 223, 217, 1370, 310, 152, 53, 112, 1283, 1500, 1028, 2841, 1348, 1119, 34, 1350, 2839,
             605, 1294, 891, 393, 573, 1043, 314, 424, 903, 1432, 722, 398, 732, 128, 219, 879, 1, 1247, 1419, 366,
             1550, 165, 1286, 399, 671, 886, 1311, 2855, 1102, 339, 93, 488, 696, 303, 1379, 1171, 727, 1532, 430, 854,
             95, 763, 1160, 1494, 5, 698, 1219, 1245, 730, 1407, 59, 1205, 795, 1512, 716, 1453, 1254, 301, 106, 676,
             401, 68, 156, 271, 1418, 1424, 1116, 56, 1309, 1159, 331, 2854, 1375, 2840, 371, 1503, 70, 914, 1255, 861,
             1491, 1033, 713, 627, 1335, 1306, 468, 1546, 1081, 78, 109, 55, 234, 818, 1391, 1235, 830, 1233, 1304, 99,
             1438, 438, 1396, 837, 902, 1484, 75, 592, 1320, 2846, 1476, 1459, 154, 1193, 882, 1517, 1393, 1421, 1178,
             327, 954, 73, 1040, 1018, 1495, 720, 1226, 1518, 1435, 1007, 1441, 1460, 181, 32, 1318, 1048, 1266, 1367,
             564, 1203, 139, 859, 1112, 193, 1185, 1041, 1351, 62, 378, 201, 971, 257, 531, 1537, 1230, 1265, 940, 953,
             832, 1429, 1322, 83, 952, 176, 182, 291, 949, 928, 1022, 133, 1451, 568, 41, 2844, 1542, 390, 793, 285,
             1552, 1274, 48, 919, 1261, 628, 1278, 1425, 114, 1325, 142, 194, 1055, 792, 31, 1192, 124, 1170, 158, 1408,
             1061, 1201, 395, 377, 1372, 249, 1014, 1204, 134, 143, 743, 1284, 207, 584, 871, 1133, 833, 330, 1405,
             1280, 1332, 1510, 2858, 110, 1449, 322, 1466, 280, 1506, 848, 1125, 2847, 260, 1297, 738, 1237, 1050, 1293,
             161, 391, 827, 284, 873, 552, 251, 1127, 1120, 1524, 970, 1183, 1392, 1514, 563, 1528, 394, 1548, 2845,
             747, 1422, 87, 846, 1181, 254, 144, 1355, 674, 164, 22, 1415, 1502, 988, 1527, 1490, 1180, 1511, 306, 617,
             1087, 43, 1123, 215, 431, 1493, 1465, 77, 1336, 1051, 1467, 1138, 24, 1186, 633, 1244, 108, 805, 1263,
             1075, 688, 1544, 541, 1331, 233, 1428, 2838, 64, 300, 950, 652, 40, 1555, 476, 560, 91, 275, 1184, 1315,
             935, 446, 1023, 599, 1496, 1439, 342, 247, 1471, 707, 632, 2, 149, 1169, 1529, 1240, 20, 858, 1327, 1481,
             92, 663, 1277, 363, 27, 1378, 166, 209, 107, 163, 414, 784, 200, 337, 939, 111, 1054, 60, 178, 1328, 417,
             1347, 373, 1049, 642, 947, 748, 416, 1161, 57, 1545, 84, 189, 1364, 913, 276, 141, 1305, 1290, 131, 680,
             145, 842, 309, 1285, 771, 63, 179, 613, 1256, 866, 918, 602, 1239, 1246, 786, 1533, 1144, 634, 256, 1241,
             900, 2859, 1376, 1470, 631, 739, 151, 212, 174, 1497, 2842}
        )

    def testMemberFromEmailSelection(self):
        self.assertListEqual(self.member.all_emails(), [('private', 'email1@email.org')])
        self.assertListEqual(self.member2.all_emails(), [
            ('general', 'info@juntagrico.juntagrico'), ('private', 'email2@email.org')
        ])
        self.assertListEqual(self.member3.all_emails(), [
            ('for_members', 'member@juntagrico.juntagrico'),
            ('for_subscriptions', 'subscription@juntagrico.juntagrico'),
            ('private', 'email3@email.org')
        ])
        self.assertListEqual(self.member4.all_emails(), [
            ('for_shares', 'share@juntagrico.juntagrico'), ('private', 'email4@email.org')
        ])
        self.assertListEqual(self.member5.all_emails(), [
            ('technical', 'it@juntagrico.juntagrico'), ('private', 'email5@email.org')
        ])
        self.assertListEqual(self.area_admin.all_emails(), [
            ('area1-m0', 'email_contact@example.org'),
            ('area2-m2', 'email2@email.org'),
            ('private', 'areaadmin@email.org')
        ])
        self.assertListEqual(self.area_admin_contact.all_emails(), [
            ('area1-m0', 'email_contact@example.org'),
            ('private', 'area_admin13@email.org')
        ])
        self.assertListEqual(self.admin.all_emails(), [
            ('general', 'info@juntagrico.juntagrico'),
            ('for_members', 'member@juntagrico.juntagrico'),
            ('for_subscriptions', 'subscription@juntagrico.juntagrico'),
            ('for_shares', 'share@juntagrico.juntagrico'),
            ('technical', 'it@juntagrico.juntagrico'),
            ('private', 'admin@email.org')
        ])

    def testMailSend(self):
        with open('juntagrico/tests/test_mailer.py') as fp:
            post_data = {
                'from_email': 'private',
                'to_list': ['all_subscriptions'],
                'to_members': [self.member.id],
                'to_areas': [self.area.id],
                'to_depots': [self.depot.id],
                'to_job': [self.job2.id],
                'copy': 'on',
                'subject': 'test',
                'attachments0': fp
            }
            if settings.ENABLE_SHARES:
                post_data['to_list'].append('all_shares')
            response = self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], 'test_mailer.py')
        expected = [
            'first_name1 last_name1 <email1@email.org>',
            'first_name3 last_name3 <email3@email.org>',
            'first_name6 last_name6 <member6@email.org>',
            'first_name7 last_name7 <member7@email.org>',
        ]
        if settings.ENABLE_SHARES:
            expected = ['First_name4 Last_name4 <email4@email.org>'] + expected
        self.assertListEqual(sorted(mail.outbox[0].bcc), expected)
        self.assertRedirects(response, reverse('email-sent'))

    @tag('shares')
    def testAllSharesMailSend(self):
        post_data = {
            'from_email': 'private',
            'to_list': ['all_shares'],
            'subject': 'test',
        }
        self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertListEqual(sorted(mail.outbox[0].bcc), [
            'First_name4 Last_name4 <email4@email.org>',
            'first_name1 last_name1 <email1@email.org>'
        ])

    def testMailTemplate(self):
        self.assertGet(reverse('email-template', args=[self.mail_template.pk]))
        self.assertGet(reverse('email-template', args=[self.mail_template.pk]), member=self.member2, code=302)

    @override_settings(EMAIL_BACKEND='juntagrico.backends.email.LocmemBatchEmailBackend')
    @patch('juntagrico.backends.email.LocmemBatchEmailBackend.send_messages', mock_batch_mailer)
    def testBatchMailer(self):
        post_data = {
            'from_email': 'private',
            'to_list': ['all_subscriptions'],
            'to_members': [1],
            'subject': 'test',
        }
        if settings.ENABLE_SHARES:
            post_data['to_list'].append('all_shares')
        self.assertPost(reverse('email-write'), post_data, code=302)
        # check that email was split into batches
        self.assertEqual(len(mail.outbox), 10 if settings.ENABLE_SHARES else 7)


@override_settings(EMAIL_BACKEND='juntagrico.backends.email.LocmemEmailBackend')
class BackendTest(TestCase):
    def make_email(self, bcc=None):
        return EmailMultiAlternatives(
            'test subject',
            'test body',
            'me from juntagrico <juntagrico@example.com>',
            bcc=bcc or ['john <john@example.com>', 'me@example.com'],
        )

    def testSendEmail(self):
        self.make_email().send()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(FROM_FILTER={
        'filter_expression': r'.*@juntagrico\.org',
        'replacement_from': 'juntagrico@juntagrico.org'
    })
    def testFromFilter(self):
        self.make_email().send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'me from juntagrico <juntagrico@juntagrico.org>')

    @override_settings(DEBUG=True)
    def testNoRecipients(self):
        self.make_email().send()
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(DEBUG=True, WHITELIST_EMAILS=['maria@example.com'])
    def testWhitelistEmail(self):
        self.make_email(['john <john@example.com>', 'maria <maria@example.com>']).send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, ['maria <maria@example.com>'])
