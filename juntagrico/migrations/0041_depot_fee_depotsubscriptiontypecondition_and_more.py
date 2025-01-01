# Generated by Django 4.2.10 on 2024-06-17 22:39

from django.db import migrations, models
import django.db.models.deletion
import juntagrico.entity


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0001_squashed_0040_post_1_6'),
    ]

    operations = [
        migrations.AddField(
            model_name='depot',
            name='fee',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Aufpreis für Mitglied', max_digits=9, verbose_name='Aufpreis'),
        ),
        migrations.CreateModel(
            name='DepotSubscriptionTypeCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.DecimalField(decimal_places=2, default=0.0, help_text='Aufpreis für Mitglied', max_digits=9, verbose_name='Aufpreis')),
                ('depot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_type_conditions', to='juntagrico.depot', verbose_name='Depot')),
                ('subscription_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='depot_conditions', to='juntagrico.subscriptiontype', verbose_name='Abo-Typ')),
            ],
            options={
                'verbose_name': 'Depot-Abo-Typ',
                'verbose_name_plural': 'Depot-Abo-Typen',
            },
            bases=(models.Model, juntagrico.entity.OldHolder),
        ),
        migrations.AddConstraint(
            model_name='depotsubscriptiontypecondition',
            constraint=models.UniqueConstraint(fields=('depot', 'subscription_type'), name='unique_depot_subscription_type'),
        ),
    ]