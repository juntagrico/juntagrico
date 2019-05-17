from test.util.test import JuntagricoTestCase


class HomeTests(JuntagricoTestCase):

    def testHome(self):
        self.assertSimpleGet('/my/home')
