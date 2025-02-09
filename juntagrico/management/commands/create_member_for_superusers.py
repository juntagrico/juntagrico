from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from juntagrico.entity.member import Member


class Command(BaseCommand):
    help = "Use this after `createsuperuser` to create a member for all super users, which is needed for login."

    # entry point used by manage.py
    def handle(self, *args, **options):
        members = Member.objects.bulk_create([
            Member(user=user, first_name='super', last_name='duper', email=user.email,
                   addr_street='superstreet', addr_zipcode='8000',
                   addr_location='SuperCity', phone='012345678', confirmed=True)
            for user in User.objects.filter(is_superuser=True, member__isnull=True)
        ])
        return f"Created {len(members)} member(s) for superusers."
