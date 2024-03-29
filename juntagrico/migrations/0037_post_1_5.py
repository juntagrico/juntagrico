# Generated by Django 3.2 on 2021-11-16 08:00
import django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0036_data_1_5'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobtype',
            name='location',
        ),
        migrations.RenameField(
            model_name='jobtype',
            old_name='location2',
            new_name='location'
        ),
        migrations.RemoveField(
            model_name='onetimejob',
            name='location',
        ),
        migrations.RenameField(
            model_name='onetimejob',
            old_name='location2',
            new_name='location'
        ),
        migrations.RemoveField(
            model_name='depot',
            name='addr_location',
        ),
        migrations.RemoveField(
            model_name='depot',
            name='addr_street',
        ),
        migrations.RemoveField(
            model_name='depot',
            name='addr_zipcode',
        ),
        migrations.RemoveField(
            model_name='depot',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='depot',
            name='longitude',
        ),
        migrations.RenameField(
            model_name='depot',
            old_name='location2',
            new_name='location'
        ),
        migrations.AlterField(
            model_name='jobtype',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location',
                                    verbose_name='Ort'),
        ),
        migrations.AlterField(
            model_name='onetimejob',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location',
                                    verbose_name='Ort'),
        ),
        migrations.AlterField(
            model_name='depot',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location',
                                    verbose_name='Ort'),
        ),
        migrations.RemoveField(
            model_name='activityarea',
            name='email',
        ),
        migrations.RemoveField(
            model_name='activityarea',
            name='show_coordinator_phonenumber',
        ),
    ]
