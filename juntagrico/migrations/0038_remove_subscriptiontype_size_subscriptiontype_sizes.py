# Generated by Django 4.0.10 on 2023-12-16 16:14

from django.db import migrations, models
import django.db.models.deletion


def make_many_sizes(apps, schema_editor):
    """
        Adds the SubscriptionSize object in SubscriptionType.size to the
        many-to-many relationship in SubscriptionType.size
    """
    SubscriptionType = apps.get_model('juntagrico', 'SubscriptionType')

    for subtype in SubscriptionType.objects.all():
        subtype.sizes.add(subtype.size)

class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0037_post_1_5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptiontype',
            name='size',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='types_old', to='juntagrico.subscriptionsize', verbose_name='Grösse'),
        ),
        migrations.AddField(
            model_name='subscriptiontype',
            name='sizes',
            field=models.ManyToManyField(related_name='types', to='juntagrico.subscriptionsize', verbose_name='Grösse'),
        ),
        migrations.RunPython(make_many_sizes),
        migrations.RemoveField(
            model_name='subscriptiontype',
            name='size',
        ),
    ]
