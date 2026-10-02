from django.test import override_settings

from . import JuntagricoTestCase
from .. import defaults
from ..config import Config


class VocabularyTests(JuntagricoTestCase):
    @override_settings(
        VOCABULARY=defaults.german(
            account=('K', 'Ks', 'f'),
            assignment=('B', 'Bs', 'n'),
            member_type=('N', 'Ns', 'm'),
            membership=('M', 'Ms', 'n'),
            share=('S', 'Ss', 'f'),
            depot=('D', 'Ds', 'f'),
            subscription=('E', 'Es', 'm'),
            co_member=('C', 'Cs', 'f'),
        )
    )
    def testGerman(self):
        self.assertEqual(Config.vocabulary('this_account'), 'diese K')
        self.assertEqual(Config.vocabulary('the_assignment_acc'), 'das B')
        self.assertEqual(Config.vocabulary('not_a_member_type'), 'kein N')
        self.assertEqual(Config.vocabulary('membership_pl'), 'Ms')
        self.assertEqual(Config.vocabulary('your_membership_acc'), 'dein M')
        self.assertEqual(Config.vocabulary('this_share_acc'), 'diese S')
        self.assertEqual(Config.vocabulary('the_depot_dat'), 'der D')
        self.assertEqual(Config.vocabulary('another_subscription_dat'), 'einem anderen E')
        self.assertEqual(Config.vocabulary('co_member'), 'C')

    @override_settings(
        VOCABULARY=defaults.french(
            depot=('D', 'Ds', 'f'),
            membership=('H', 'Hs', 'f'),  # h muet
            subscription=('H', 'Hs', 'F'),  # h aspiré
        )
    )
    def testFrench(self):
        self.assertEqual(Config.vocabulary('the_depot_dat'), 'à la D')
        self.assertEqual(Config.vocabulary('your_membership_acc'), 'ton H')
        self.assertEqual(Config.vocabulary('your_subscription'), 'ta H')


@override_settings(
    VOCABULARY={
        'fr': defaults.french(
            account=('K', 'Ks', 'f'),
            assignment=('B', 'Bs', 'f'),
            member_type=('N', 'Ns', 'm'),
            membership=('M', 'Ms', 'm'),
            share=('A', 'As', 'm'),
            depot=('H', 'Hs', 'f'),
            subscription=('E', 'Es', 'm'),
        )
    }
)
class VocabularyMultipleLanguagesTests(JuntagricoTestCase):
    def testGerman(self):
        # should be unchanged
        self.assertEqual(Config.vocabulary('this_account'), 'dieses Konto')
        self.assertEqual(Config.vocabulary('another_subscription_dat'), 'einem anderen Abo')

    @override_settings(LANGUAGE_CODE='fr')
    def testFrench(self):
        self.assertEqual(Config.vocabulary('this_account'), 'cette K')
        self.assertEqual(Config.vocabulary('the_assignment_acc'), 'la B')
        self.assertEqual(Config.vocabulary('not_a_member_type'), 'un N')
        self.assertEqual(Config.vocabulary('membership_pl'), 'Ms')
        self.assertEqual(Config.vocabulary('your_membership_acc'), 'ton M')
        self.assertEqual(Config.vocabulary('this_share_acc'), 'cet A')
        self.assertEqual(Config.vocabulary('the_depot_acc'), 'l\'H')
        self.assertEqual(Config.vocabulary('the_depot_dat'), 'à l\'H')
        self.assertEqual(Config.vocabulary('another_subscription_dat'), 'à un autre E')
