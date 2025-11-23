from django.db import migrations, models
import django.db.models.deletion
import juntagrico


def has_perm(apps, user, perm):
    permission = apps.get_model('auth', 'Permission')
    perm = permission.objects.get(codename=perm)
    return user.user_permissions.filter(codename=perm.codename).exists() or user.groups.filter(permissions=perm).exists()


def migrate_coordinators(apps, schema_editor):
    depots = apps.get_model('juntagrico', 'Depot')
    depot_coordinator = apps.get_model('juntagrico', 'DepotCoordinator')
    user = apps.get_model('auth', 'User')
    for depot in depots.objects.all():
        coordinator = user.objects.get(pk=depot.contact.user.pk)
        is_depot_admin = has_perm(apps, coordinator, 'is_depot_admin')
        can_change_depot = has_perm(apps, coordinator, 'change_depot')
        depot_coordinator.objects.create(
            depot=depot,
            member=depot.contact,
            can_modify_depot=can_change_depot,
            can_view_member=is_depot_admin,
            can_contact_member=is_depot_admin,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0045_alter_activityarea_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='depot',
            options={'ordering': ['sort_order'], 'verbose_name': 'Depot', 'verbose_name_plural': 'Depots'},
        ),
        migrations.CreateModel(
            name='DepotCoordinator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_modify_depot', models.BooleanField(default=True, verbose_name='Kann Beschreibung ändern')),
                ('can_view_member', models.BooleanField(default=True, verbose_name='Kann Mitglieder sehen')),
                ('can_contact_member', models.BooleanField(default=True, verbose_name='Kann Mitglieder kontaktieren')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
                ('depot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coordinator_access', to='juntagrico.depot')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='depot_access', to='juntagrico.member')),
            ],
            options={
                'verbose_name': 'Koordinator',
                'verbose_name_plural': 'Koordinatoren',
                'ordering': ['sort_order'],
            },
            bases=(models.Model, juntagrico.entity.OldHolder),
        ),
        migrations.AddField(
            model_name='depot',
            name='coordinators',
            field=models.ManyToManyField(related_name='coordinated_depots', through='juntagrico.DepotCoordinator', to='juntagrico.member', verbose_name='Koordinatoren'),
        ),
        migrations.AddConstraint(
            model_name='depotcoordinator',
            constraint=models.UniqueConstraint(fields=('depot', 'member'), name='unique_depot_member'),
        ),
        migrations.RunPython(migrate_coordinators),
    ]
