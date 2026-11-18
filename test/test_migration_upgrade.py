#!/usr/bin/env python
"""
Test the migration upgrade path from an old database with Billable to the new schema.

This script tests the real production upgrade path:
1. Replace the current squashed migration with the original version (that includes Billable)
   from test/0001_squashed_0051_initial.py
2. Migrate through the squashed migration + remaining migrations (→ 0064)
   so the database schema matches what production databases look like today
3. Insert test data
4. Restore the current squashed migration, then apply migration 0065 (Billable removal)
5. Verify data preservation via Django ORM

Intended for CI use to test the migration upgrade path on PostgreSQL and MySQL.
Run with: python test/test_migration_upgrade.py
(Requires DJANGO_SETTINGS_MODULE to be set to a PostgreSQL or MySQL config.)
"""
import os
import shutil
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')

import django  # noqa: E402
django.setup()

from django.db import connection  # noqa: E402


# Path to the migrations directory
MIGRATIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'juntagrico', 'migrations'
)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SQUASHED_MIGRATION = '0001_squashed_0051_initial.py'
ORIGINAL_SQUASHED = os.path.join(TEST_DIR, SQUASHED_MIGRATION)
CURRENT_SQUASHED = os.path.join(MIGRATIONS_DIR, SQUASHED_MIGRATION)
BACKUP_SQUASHED = os.path.join(MIGRATIONS_DIR, '.0001_squashed_0051_initial.py.bak')


def replace_squashed_with_original():
    """Replace the current squashed migration with the original version that includes Billable."""
    # Backup the current squashed migration
    if os.path.exists(CURRENT_SQUASHED):
        shutil.copy2(CURRENT_SQUASHED, BACKUP_SQUASHED)
    # Copy the original squashed migration (with Billable) into place
    shutil.copy2(ORIGINAL_SQUASHED, CURRENT_SQUASHED)
    print('  Replaced squashed migration with original (includes Billable)')


def restore_current_squashed():
    """Restore the current squashed migration from backup."""
    if os.path.exists(BACKUP_SQUASHED):
        shutil.move(BACKUP_SQUASHED, CURRENT_SQUASHED)
        print('  Restored current squashed migration')
    elif not os.path.exists(CURRENT_SQUASHED):
        # Fallback: copy original back if backup was lost
        shutil.copy2(ORIGINAL_SQUASHED, CURRENT_SQUASHED)
        print('  Restored squashed migration (fallback)')


def insert_test_data():
    """Insert test data using raw SQL into the old schema with Billable."""
    from django.contrib.auth.hashers import make_password
    from django.utils import timezone

    # Clean up any leftover test data from previous runs (respect FK order)
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM juntagrico_share WHERE member_id IN (
                SELECT id FROM juntagrico_member WHERE user_id IN (
                    SELECT id FROM auth_user WHERE username = %s
                )
            ) OR billable_ptr_id IN (%s, %s, %s, %s)
        """, ['test_migration', 100, 101, 102, 103])
        cursor.execute("""
            DELETE FROM juntagrico_subscription WHERE primary_member_id IN (
                SELECT id FROM juntagrico_member WHERE user_id IN (
                    SELECT id FROM auth_user WHERE username = %s
                )
            ) OR depot_id IN (
                SELECT id FROM juntagrico_depot WHERE name = %s
            ) OR billable_ptr_id IN (%s, %s, %s, %s)
        """, ['test_migration', 'Test Depot', 100, 101, 102, 103])
        cursor.execute("DELETE FROM juntagrico_billable WHERE id IN (%s, %s, %s, %s)",
                       [100, 101, 102, 103])
        # Delete in FK order: subscriptiontype -> bundle_product_size junction -> subscriptionbundle -> productsize -> subscriptionproduct
        cursor.execute("DELETE FROM juntagrico_subscriptiontype WHERE name = %s", ['Test Type'])
        cursor.execute("""
            DELETE FROM juntagrico_subscriptionbundleproductsize
            WHERE product_size_id IN (SELECT id FROM juntagrico_productsize WHERE product_id IN (SELECT id FROM juntagrico_subscriptionproduct WHERE name = %s))
        """, ['Test Product'])
        cursor.execute("DELETE FROM juntagrico_subscriptionbundle WHERE long_name = %s", ['Test Bundle'])
        cursor.execute("""
            DELETE FROM juntagrico_productsize
            WHERE product_id IN (SELECT id FROM juntagrico_subscriptionproduct WHERE name = %s)
        """, ['Test Product'])
        cursor.execute("DELETE FROM juntagrico_subscriptionproduct WHERE name = %s", ['Test Product'])
        cursor.execute("DELETE FROM juntagrico_depot WHERE name = %s", ['Test Depot'])
        cursor.execute("DELETE FROM juntagrico_location WHERE name = %s", ['Test Location'])
        cursor.execute("""
            DELETE FROM juntagrico_member WHERE user_id IN (
                SELECT id FROM auth_user WHERE username = %s
            )
        """, ['test_migration'])
        cursor.execute("DELETE FROM auth_user WHERE username = %s", ['test_migration'])

    # Create test data using raw SQL to avoid signal triggers and MySQL strict mode issues
    now = timezone.now()
    vendor = connection.vendor

    with connection.cursor() as cursor:
        # auth_user
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO auth_user (username, first_name, last_name, password, email,
                                       is_staff, is_superuser, is_active, date_joined, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, ['test_migration', '', '', make_password('password'), 'test_migration@email.org',
                  False, False, True, now, now])
        else:
            cursor.execute("""
                INSERT INTO auth_user (username, first_name, last_name, password, email,
                                       is_staff, is_superuser, is_active, date_joined, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ['test_migration', '', '', make_password('password'), 'test_migration@email.org',
                  False, False, True, now, now])
            cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()[0]

        # juntagrico_member (include all NOT NULL fields)
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_member (first_name, last_name, email, addr_street,
                                               addr_zipcode, addr_location, phone, iban,
                                               confirmed, reachable_by_email, notes,
                                               signup_comment, user_id, cancellation_comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, ['Test', 'Member', 'test_migration@email.org', 'Teststrasse', '1234',
                  'Teststadt', '', '', True, True, '', '', user_id, ''])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_member (first_name, last_name, email, addr_street,
                                               addr_zipcode, addr_location, phone, iban,
                                               confirmed, reachable_by_email, notes,
                                               signup_comment, user_id, cancellation_comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ['Test', 'Member', 'test_migration@email.org', 'Teststrasse', '1234',
                  'Teststadt', '', '', True, True, '', '', user_id, ''])
            cursor.execute("SELECT LAST_INSERT_ID()")
        member_id = cursor.fetchone()[0]

        # juntagrico_location
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_location (name, description, visible, sort_order)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, ['Test Location', '', True, 0])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_location (name, description, visible, sort_order)
                VALUES (%s, %s, %s, %s)
            """, ['Test Location', '', True, 0])
            cursor.execute("SELECT LAST_INSERT_ID()")
        location_id = cursor.fetchone()[0]

        # juntagrico_depot
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_depot (name, weekday, location_id, capacity, fee,
                                              description, access_information, depot_list,
                                              visible, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, ['Test Depot', 1, location_id, 10, 0, '', '', False, True, 0])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_depot (name, weekday, location_id, capacity, fee,
                                              description, access_information, depot_list,
                                              visible, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ['Test Depot', 1, location_id, 10, 0, '', '', False, True, 0])
            cursor.execute("SELECT LAST_INSERT_ID()")
        depot_id = cursor.fetchone()[0]

        # juntagrico_subscriptionproduct
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_subscriptionproduct (name, description, sort_order)
                VALUES (%s, %s, %s) RETURNING id
            """, ['Test Product', 'Test', 0])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_subscriptionproduct (name, description, sort_order)
                VALUES (%s, %s, %s)
            """, ['Test Product', 'Test', 0])
            cursor.execute("SELECT LAST_INSERT_ID()")
        product_id = cursor.fetchone()[0]

        # juntagrico_productsize
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_productsize (name, product_id, units, show_on_depot_list, sort_order)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, ['4', product_id, 1, True, 4.0])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_productsize (name, product_id, units, show_on_depot_list, sort_order)
                VALUES (%s, %s, %s, %s, %s)
            """, ['4', product_id, 1, True, 4.0])
            cursor.execute("SELECT LAST_INSERT_ID()")
        size_id = cursor.fetchone()[0]

        # juntagrico_subscriptionbundle
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_subscriptionbundle (long_name, description, sort_order)
                VALUES (%s, %s, %s) RETURNING id
            """, ['Test Bundle', 'Test', 0])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_subscriptionbundle (long_name, description, sort_order)
                VALUES (%s, %s, %s)
            """, ['Test Bundle', 'Test', 0])
            cursor.execute("SELECT LAST_INSERT_ID()")
        bundle_id = cursor.fetchone()[0]

        # juntagrico_subscriptionbundleproductsize
        cursor.execute("""
            INSERT INTO juntagrico_subscriptionbundleproductsize (bundle_id, product_size_id)
            VALUES (%s, %s)
        """, [bundle_id, size_id])

        # juntagrico_subscriptiontype
        if vendor == 'postgresql':
            cursor.execute("""
                INSERT INTO juntagrico_subscriptiontype (name, long_name, shares, required_assignments,
                                                         required_core_assignments, price, visible, is_extra,
                                                         trial, trial_days, description, sort_order, "interval",
                                                         "offset", bundle_id, requires_membership)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ['Test Type', 'Test Type', 0, 0, 0, 100, True, False, False, 0, 'Test', 1.0,
                   0, 0, bundle_id, False])
        else:
            cursor.execute("""
                INSERT INTO juntagrico_subscriptiontype (name, long_name, shares, required_assignments,
                                                         required_core_assignments, price, visible, is_extra,
                                                         trial, trial_days, description, sort_order, `interval`,
                                                         `offset`, bundle_id, requires_membership)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ['Test Type', 'Test Type', 0, 0, 0, 100, True, False, False, 0, 'Test', 1.0,
                   0, 0, bundle_id, False])

    share1_id = 100
    share2_id = 101
    sub1_id = 102
    sub2_id = 103

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO juntagrico_billable (id, polymorphic_ctype_id)
            VALUES (%s, NULL), (%s, NULL), (%s, NULL), (%s, NULL)
        """, [share1_id, share2_id, sub1_id, sub2_id])

        now = timezone.now().date()
        cursor.execute("""
            INSERT INTO juntagrico_share
            (billable_ptr_id, value, creation_date, paid_date, issue_date,
             booking_date, cancelled_date, termination_date, payback_date,
             number, sent_back, reason_for_acquisition, reason_for_cancellation,
             notes, member_id)
            VALUES (%s, 0, %s, '2020-01-15', '2020-01-01',
                    NULL, NULL, NULL, NULL,
                    NULL, FALSE, NULL, NULL, '', %s),
                   (%s, 0, %s, '2021-01-15', '2021-01-01',
                    NULL, NULL, NULL, NULL,
                    NULL, FALSE, NULL, NULL, '', %s)
        """, [share1_id, now, member_id, share2_id, now, member_id])

        cursor.execute("""
            INSERT INTO juntagrico_subscription
            (billable_ptr_id, creation_date, activation_date, cancellation_date,
             deactivation_date, nickname, start_date, end_date, notes, depot_id,
             future_depot_id, primary_member_id, identifier)
            VALUES (%s, %s, %s, NULL, NULL, '', %s, NULL, '', %s, NULL, %s, 'sub1'),
                   (%s, %s, NULL, NULL, NULL, '', %s, NULL, '', %s, NULL, %s, 'sub2')
        """, [sub1_id, now, now, now, depot_id, member_id,
              sub2_id, now, now, depot_id, member_id])

    return {
        'share1_id': share1_id,
        'share2_id': share2_id,
        'sub1_id': sub1_id,
        'sub2_id': sub2_id,
        'member_id': member_id,
        'depot_id': depot_id,
    }


def migrate_to(target_app, target_name):
    """Migrate to a specific migration using Django's MigrationExecutor."""
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    executor.migrate([(target_app, target_name)])


def main():
    if connection.vendor == 'sqlite':
        print('ERROR: SQLite is not supported in production. Run this on PostgreSQL or MySQL.')
        sys.exit(1)

    # Step 1: Replace squashed migration with original and migrate to 0064
    print('Step 1: Migrating with original squashed migration (includes Billable) → 0064...')
    replace_squashed_with_original()
    try:
        migrate_to('juntagrico', '0064_alter_specialroles_options')
        print('✓ Migrated to 0064')
    finally:
        # Restore the current squashed migration before continuing
        restore_current_squashed()

    # Step 2: Insert test data
    print('Step 2: Inserting test data...')
    ids = insert_test_data()
    share1_id, share2_id, sub1_id, sub2_id = ids['share1_id'], ids['share2_id'], ids['sub1_id'], ids['sub2_id']
    member_id = ids['member_id']
    depot_id = ids['depot_id']
    print('✓ Test data inserted')

    # Step 3: Apply migration 0065 (Billable removal)
    print('Step 3: Applying migration 0065 (Billable removal)...')
    migrate_to('juntagrico', '0065_remove_billable')
    print('✓ Migration 0065 applied')

    # Step 4: Verify data preservation via Django ORM
    print('Step 4: Verifying data preservation and operations via Django ORM...')
    errors = []

    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    from juntagrico.entity.share import Share
    from juntagrico.entity.subs import Subscription
    from juntagrico.entity.member import Member
    from juntagrico.entity.depot import Depot

    share_count = Share.objects.count()
    sub_count = Subscription.objects.count()
    if share_count != 2:
        errors.append(f'Share count: expected 2, got {share_count}')
    if sub_count != 2:
        errors.append(f'Subscription count: expected 2, got {sub_count}')

    try:
        share1 = Share.objects.get(pk=share1_id)
        if share1.member_id != member_id:
            errors.append(f'Share {share1_id} member_id mismatch')
        if str(share1.issue_date) != '2020-01-01':
            errors.append(f'Share {share1_id} issue_date mismatch')
        if share1.member.first_name != 'Test':
            errors.append(f'Share {share1_id} member relation traversal failed')
    except Share.DoesNotExist:
        errors.append(f'Share {share1_id} not found')
    except Exception as e:
        errors.append(f'Share {share1_id} relation error: {e}')

    try:
        share2 = Share.objects.get(pk=share2_id)
        if str(share2.issue_date) != '2021-01-01':
            errors.append(f'Share {share2_id} issue_date mismatch')
    except Share.DoesNotExist:
        errors.append(f'Share {share2_id} not found')
    except Exception as e:
        errors.append(f'Share {share2_id} relation error: {e}')

    try:
        sub1 = Subscription.objects.get(pk=sub1_id)
        if sub1.depot_id != depot_id:
            errors.append(f'Subscription {sub1_id} depot_id mismatch')
        if sub1.depot.name != 'Test Depot':
            errors.append(f'Subscription {sub1_id} depot relation traversal failed')
        if sub1.primary_member.first_name != 'Test':
            errors.append(f'Subscription {sub1_id} primary_member relation traversal failed')
    except Subscription.DoesNotExist:
        errors.append(f'Subscription {sub1_id} not found')
    except Exception as e:
        errors.append(f'Subscription {sub1_id} relation error: {e}')

    try:
        sub2 = Subscription.objects.get(pk=sub2_id)
        if sub2.depot_id != depot_id:
            errors.append(f'Subscription {sub2_id} depot_id mismatch')
    except Subscription.DoesNotExist:
        errors.append(f'Subscription {sub2_id} not found')
    except Exception as e:
        errors.append(f'Subscription {sub2_id} relation error: {e}')

    # Verify querysets and filtering
    try:
        shares_for_member = Share.objects.filter(member_id=member_id)
        if shares_for_member.count() != 2:
            errors.append(f'Share.objects.filter(member_id=...) returned {shares_for_member.count()} shares, expected 2')
        subs_for_depot = Subscription.objects.filter(depot_id=depot_id)
        if subs_for_depot.count() != 2:
            errors.append(f'Subscription.objects.filter(depot_id=...) returned {subs_for_depot.count()} subs, expected 2')
    except Exception as e:
        errors.append(f'Queryset filtering error: {e}')

    # Verify ContentTypes and Permissions
    for model_name in ('share', 'subscription'):
        ct = ContentType.objects.filter(app_label='juntagrico', model=model_name).first()
        if not ct:
            errors.append(f'ContentType for juntagrico.{model_name} missing')
        else:
            perm_count = Permission.objects.filter(content_type=ct).count()
            if perm_count < 4:
                errors.append(f'Expected at least 4 permissions for {model_name}, found {perm_count}')

    # Verify creating new Share and Subscription records (tests auto-increment / identity sequence)
    try:
        member = Member.objects.get(pk=member_id)
        depot = Depot.objects.get(pk=depot_id)

        new_share = Share.objects.create(
            member=member,
            value=200,
        )
        if new_share.id <= max(share1_id, share2_id):
            errors.append(f'New Share id {new_share.id} not greater than existing max ID {max(share1_id, share2_id)}')

        new_sub = Subscription.objects.create(
            depot=depot,
            primary_member=member,
        )
        if new_sub.id <= max(sub1_id, sub2_id):
            errors.append(f'New Subscription id {new_sub.id} not greater than existing max ID {max(sub1_id, sub2_id)}')

        # Clean up the newly created test records
        new_share.delete()
        new_sub.delete()
    except Exception as e:
        errors.append(f'Error creating new Share/Subscription post-migration: {e}')

    if errors:
        for error in errors:
            print(f'✗ {error}')
        print('Migration upgrade test FAILED!')
        sys.exit(1)

    print('✓ All checks passed! Migration upgrade path is working correctly.')


if __name__ == '__main__':
    main()
