# Generated by Django 4.0.1 on 2022-02-08 21:44

from django.db import migrations
from juntagrico.util.temporal import weekdays
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q


def set_location_sort_order(apps, schema_editor):
    location = apps.get_model('juntagrico', 'Location')
    for idx, item in enumerate(location.objects.all()):
        item.sort_order = idx + 1
        item.save()


def make_name_product_unique(apps, schema_editor):
    SubscriptionSize = apps.get_model('juntagrico', 'SubscriptionSize')
    taken = set()
    for size in SubscriptionSize.objects.all():
        while (size.name, size.product) in taken:
            size.name += str(size.id)
        size.save()
        taken.add((size.name, size.product))


def set_tour(apps, schema_editor):
    depot = apps.get_model('juntagrico', 'Depot')
    tour = apps.get_model('juntagrico', 'Tour')
    delivery = apps.get_model('juntagrico', 'Delivery')
    for d in depot.objects.all():
        if 8 > d.weekday > 0:
            d.tour = tour.objects.get_or_create(name=weekdays[d.weekday])[0]
            d.save()
    for d in delivery.objects.all():
        d.tour = tour.objects.get_or_create(name=weekdays[d.delivery_date.weekday() + 1])[0]
        d.save()


def mail_send_permissions_forward(apps, schema_editor):
    """Add new permissions to all groups and users with can_send_mails permission"""
    # create permissions so that they can be added
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None
    # get relevant new send mail permissions from juntagrico
    perm_new = Permission.objects.filter(Q(content_type__app_label='juntagrico') & (
            Q(codename='can_email_all_in_system') |
            Q(codename='can_email_all_with_share') |
            Q(codename='can_email_all_with_sub') |
            Q(codename='can_email_free_address_list')))
    # get old can_send_mails permission
    perm_old = Permission.objects.get(Q(content_type__app_label='juntagrico') & Q(codename='can_send_mails'))
    # add new permissions to all groups with old permission
    groups = Group.objects.filter(permissions=perm_old)
    for group in groups:
        for perm in perm_new:
            group.permissions.add(perm)
    # add new permissions to all users with old permission
    users = User.objects.filter(user_permissions=perm_old)
    for user in users:
        for perm in perm_new:
            user.user_permissions.add(perm)


def mail_send_permissions_backward(apps, schema_editor):
    """Delete permissions added above"""
    Permission.objects.filter(Q(content_type__app_label='juntagrico') & (
            Q(codename='can_email_all_in_system') |
            Q(codename='can_email_all_with_share') |
            Q(codename='can_email_all_with_sub') |
            Q(codename='can_email_free_address_list'))).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0038_pre_1_6'),
    ]

    operations = [
        migrations.RunPython(set_location_sort_order),
        migrations.RunPython(make_name_product_unique),
        migrations.RunPython(set_tour),
        migrations.RunPython(mail_send_permissions_forward, mail_send_permissions_backward),
    ]
