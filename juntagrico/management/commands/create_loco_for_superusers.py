from django.core.management.base import BaseCommand, CommandError

from juntagrico.models import *



class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
       for user in User.objects.all():
           if user.is_superuser:
               signals.post_save.disconnect(Loco.create, sender=Loco)
               loco = Loco.objects.create(user=user, first_name="super", last_name="duper", email=user.email, addr_street="superstreet", addr_zipcode="8000",
                                   addr_location="SuperCity", phone="012345678")
               loco.save()
               user.loco = loco
               user.save()
               signals.post_save.connect(Loco.create, sender=Loco)


