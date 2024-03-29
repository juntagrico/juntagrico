# Generated by Django 3.2 on 2021-11-16 07:59

from django.db import migrations, models
import django.db.models.deletion
import juntagrico.entity


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('juntagrico', '0034_auto_20210415_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='email',
            field=juntagrico.entity.LowercaseEmailField(max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='member',
            name='number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Mitglieder-Nummer'),

        ),
        migrations.AlterField(
            model_name='subscriptiontype',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Preis'),
        ),
        migrations.AddField(
            model_name='activityarea',
            name='auto_add_new_members',
            field=models.BooleanField(default=False, help_text='Neue Benutzer werden automatisch zu diesem Tätigkeitsbereich hinzugefügt.', verbose_name='Standard Tätigkeitesbereich für neue Benutzer'),
        ),
        migrations.AlterField(
            model_name='depot',
            name='description',
            field=models.TextField(blank=True, default='', max_length=1000, verbose_name='Beschreibung'),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('latitude',
                 models.DecimalField(blank=True, decimal_places=6, max_digits=9, max_length=100, null=True,
                                     verbose_name='Breitengrad')),
                ('longitude',
                 models.DecimalField(blank=True, decimal_places=6, max_digits=9, max_length=100, null=True,
                                     verbose_name='Längengrad')),
                ('addr_street', models.CharField(blank=True, max_length=100, null=True, verbose_name='Strasse & Nr.')),
                ('addr_zipcode', models.CharField(blank=True, max_length=10, null=True, verbose_name='PLZ')),
                ('addr_location', models.CharField(blank=True, max_length=50, null=True, verbose_name='Ort')),
                ('description', models.TextField(blank=True, default='', max_length=1000, verbose_name='Beschreibung')),
                ('visible', models.BooleanField(default=True, verbose_name='Sichtbar', help_text='Ort steht bei Einsatz und Depot zur Auswahl')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
            ],
            options={
                'verbose_name': 'Ort',
                'verbose_name_plural': 'Orte',
                'ordering': ['sort_order'],
            },
            bases=(models.Model, juntagrico.entity.OldHolder),
        ),
        migrations.AddField(
            model_name='jobtype',
            name='location2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location',
                                    verbose_name='Ort', null=True),
        ),
        migrations.AddField(
            model_name='onetimejob',
            name='location2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location',
                                    verbose_name='Ort', null=True),
        ),
        migrations.AddField(
            model_name='depot',
            name='location2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.location', null=True),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.BigIntegerField()),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Kontakt',
                'verbose_name_plural': 'Kontakte',
                'ordering': ['sort_order'],
            },
            bases=(models.Model, juntagrico.entity.OldHolder),
        ),
        migrations.CreateModel(
            name='EmailContact',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='juntagrico.contact')),
                ('email', models.EmailField(max_length=254, verbose_name='E-Mail')),
            ],
            options={
                'verbose_name': 'E-Mail-Adresse',
                'verbose_name_plural': 'E-Mail-Adresse',
            },
            bases=('juntagrico.contact',),
        ),
        migrations.CreateModel(
            name='PhoneContact',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='juntagrico.contact')),
                ('phone', models.CharField(max_length=50, verbose_name='Telefonnummer')),
            ],
            options={
                'verbose_name': 'Telefonnummer',
                'verbose_name_plural': 'Telefonnummer',
            },
            bases=('juntagrico.contact',),
        ),
        migrations.CreateModel(
            name='TextContact',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='juntagrico.contact')),
                ('text', models.TextField(verbose_name='Kontaktbeschrieb')),
            ],
            options={
                'verbose_name': 'Freier Kontaktbeschrieb',
                'verbose_name_plural': 'Freie Kontaktbeschriebe',
            },
            bases=('juntagrico.contact',),
        ),
        migrations.CreateModel(
            name='MemberContact',
            fields=[
                ('contact_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='juntagrico.contact')),
                ('display', models.CharField(choices=[('E', 'E-Mail'), ('T', 'Telefonnummer'), ('B', 'E-Mail & Telefonnummer')], default='E', max_length=1, verbose_name='Anzeige')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='juntagrico.member', verbose_name='Mitglied')),
            ],
            options={
                'verbose_name': 'Mitglied',
                'verbose_name_plural': 'Mitglieder',
            },
            bases=('juntagrico.contact',),
        ),
        migrations.AlterField(
            model_name='billable',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                    to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='job',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                    to='contenttypes.contenttype'),
        ),
    ]
