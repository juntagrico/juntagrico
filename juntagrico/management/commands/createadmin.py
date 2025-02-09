from django.db.models import signals
from django.contrib.auth.models import User
from django.contrib.auth.management.commands import createsuperuser
from juntagrico.entity.member import Member


class Command(createsuperuser.Command):
    help = "Use this instead of `createsuperuser` to create a super user with member."

    @staticmethod
    def _create_member(sender, **kwargs):
        user = kwargs['instance']
        if not hasattr(user, 'member'):
            Member.objects.bulk_create([
                Member(user=user, first_name='super', last_name=user.username, email=user.email,
                       addr_street='superstreet', addr_zipcode='8000',
                       addr_location='SuperCity', phone='012345678', confirmed=True)
            ])

    # entry point used by manage.py
    def handle(self, *args, **options):
        signals.post_save.connect(self._create_member, sender=User)
        try:
            super().handle(*args, **options)
        finally:
            signals.post_save.disconnect(self._create_member, sender=User)
