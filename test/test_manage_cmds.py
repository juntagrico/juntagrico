from io import StringIO

from django.core.management import call_command

from test.util.test import JuntagricoTestCase


class CreateMemberForSuperuserTest(JuntagricoTestCase):

    def test_create_member_for_superuser(self):
        call_command('createsuperuser', username='testsuperuer', email='super@mail.com', no_input='')
        out = StringIO()
        call_command('create_member_for_superusers', stdout=out)
        self.assertEqual(out.getvalue(), '')
