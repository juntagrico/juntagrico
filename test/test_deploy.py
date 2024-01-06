from django.core.management import call_command
from django.test import TestCase


class DeploymentTests(TestCase):

    def testCollectStatic(self):
        call_command('collectstatic', '--noinput', '-c')
