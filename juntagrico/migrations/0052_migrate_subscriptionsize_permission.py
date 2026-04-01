# migrate permissions from SubscriptionSize -> SubscriptionBundle
from django.db import migrations


def transfer_perms(apps, old_model, new_model, app_label, remove=True):
    """ Transfer permissions for those who already applied the previous migrations.
    For new migrations, the permission is updated using management.inject_rename_permissions
    """
    Permission = apps.get_model('auth', 'Permission')
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    # Permission codenames for standard model perms
    for action in ('add', 'change', 'delete', 'view'):
        old_perm = Permission.objects.filter(codename=f"{action}_{old_model}",
                                             content_type__app_label=app_label).first()
        new_perm = Permission.objects.filter(codename=f"{action}_{new_model}",
                                             content_type__app_label=app_label).first()

        print(old_perm, new_perm)
        if old_perm and new_perm:
            # Assign to users: add new permission to users who have the old permission
            for user in User.objects.filter(user_permissions=old_perm):
                user.user_permissions.add(new_perm)

            # Assign to groups: add new permission to groups who have the old permission
            for group in Group.objects.filter(permissions=old_perm):
                group.permissions.add(new_perm)

            if remove:
                # After copying, delete old permissions that exist
                try:
                    old_perm.delete()
                except Exception:
                    # ignore deletion errors to avoid migration failure; permission might be referenced elsewhere
                    pass


def forwards_func(apps, schema_editor):
    transfer_perms(apps, 'subscriptionsize', 'subscriptionbundle', 'juntagrico')
    # remove unused permissions
    Permission = apps.get_model('auth', 'Permission')
    try:
        Permission.objects.filter(codename__in=('is_area_admin', 'is_depot_admin'),
                                  content_type__app_label='juntagrico').delete()
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0051_tour_weekday'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
