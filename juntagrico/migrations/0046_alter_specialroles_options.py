# Generated by Django 4.2.17 on 2024-12-22 15:20

from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import User, Group, Permission
from django.db import migrations
from django.db.models import Q


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
        ('juntagrico', '0045_job_members'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specialroles',
            options={'default_permissions': (), 'managed': False, 'permissions': (
            ('is_operations_group', 'Ist in der BG'), ('is_book_keeper', 'Ist Buchhalter'),
            ('can_send_mails', 'Kann E-Mails versenden'),
            ('can_use_general_email', 'Kann Haupt-E-Mail-Adresse verwenden'),
            ('can_use_for_members_email', 'Kann E-Mail-Adresse "for_members" verwenden'),
            ('can_use_for_subscriptions_email', 'Kann E-Mail-Adresse "for_subscription" verwenden'),
            ('can_use_for_shares_email', 'Kann E-Mail-Adresse "for_shares" verwenden'),
            ('can_use_technical_email', 'Kann technische E-Mail-Adresse verwenden'),
            ('can_email_all_in_system', 'Kann E-Mails an alle im System senden'),
            ('can_email_all_with_share', 'Kann E-Mails an alle mit Anteilschein senden'),
            ('can_email_all_with_sub', 'Kann E-Mails an alle mit Abo senden'),
            ('can_email_free_address_list', 'Kann E-Mails frei an Adressen senden'),
            ('depot_list_notification', 'Benutzer wird bei Depot-Listen-Erstellung informiert'),
            ('can_view_exports', 'Kann Exporte öffnen'), ('can_view_lists', 'Kann Listen öffnen'),
            ('can_generate_lists', 'Kann Listen erzeugen'))},
        ),
        migrations.RunPython(mail_send_permissions_forward, mail_send_permissions_backward),
    ]
