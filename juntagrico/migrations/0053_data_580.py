from django.db import migrations
from django.db.models import Max

from juntagrico.config import Config


def initialize_membership(apps, schema_editor):
    members = apps.get_model('juntagrico', 'Member')
    memberships = apps.get_model('juntagrico', 'Membership')
    if Config.enable_shares():
        for member in members.objects.filter(user__isnull=False, share__isnull=False).distinct().order_by('user__date_joined'):
            dates = member.share_set.aggregate(
                cancellation_date=Max("cancelled_date"),
                deactivation_date=Max("termination_date"),
            )
            if member.share_set.filter(cancelled_date__isnull=True).exists():
                dates['cancellation_date'] = None
            if member.share_set.filter(termination_date__isnull=True).exists():
                dates['deactivation_date'] = None
            memberships.objects.create(
                account=member,
                activation_date=member.user.date_joined.date(),
                **dates
            )
    else:
        for member in members.objects.filter(user__isnull=False).order_by('user__date_joined'):
            memberships.objects.create(
                account=member,
                activation_date=member.user.date_joined.date(),
                cancellation_date=member.cancellation_date,
                deactivation_date=member.deactivation_date,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0052_alter_member_options_alter_membercontact_options_and_more'),
    ]

    operations = [
        migrations.RunPython(initialize_membership),
    ]
