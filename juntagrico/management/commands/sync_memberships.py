from django.core.management.base import BaseCommand

from juntagrico.entity.member import Member
from juntagrico.lifecycle.membership import sync


class Command(BaseCommand):
    help = ("Synchronizes memberships with share ownerships")

    # entry point used by manage.py
    def handle(self, *args, **options):
        for account in Member.objects.all():
            sync(None, account)
