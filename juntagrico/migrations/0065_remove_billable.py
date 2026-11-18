# Migration to remove the Billable polymorphic base class
# Billable was a PolymorphicModel with only an id and polymorphic_ctype field.
# Share and Subscription inherited from it via billable_ptr (OneToOneField PK).
# This migration converts them to regular models with their own id field.

from django.db import migrations, models
from django.db.migrations.operations.base import Operation


def ensure_content_types(apps, schema_editor):
    """Ensure Share and Subscription ContentTypes and permissions exist after removing Billable."""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    for app_label, model_name in [('juntagrico', 'share'), ('juntagrico', 'subscription')]:
        ct, created = ContentType.objects.get_or_create(
            app_label=app_label,
            model=model_name,
        )
        # Create default permissions (view, add, change, delete)
        for codename, name in [
            (f'view_{model_name}', f'Can view {model_name}'),
            (f'add_{model_name}', f'Can add {model_name}'),
            (f'change_{model_name}', f'Can change {model_name}'),
            (f'delete_{model_name}', f'Can delete {model_name}'),
        ]:
            Permission.objects.get_or_create(
                codename=codename,
                content_type=ct,
                defaults={'name': name},
            )
        # Create custom permissions defined in the model Meta
        if model_name == 'share':
            for codename, name in [
                ('notified_on_share_creation', 'Wird bei Anteilschein Erstellung informiert'),
                ('notified_on_share_cancellation', 'Wird bei Anteilschein Kündigung informiert'),
            ]:
                Permission.objects.get_or_create(
                    codename=codename,
                    content_type=ct,
                    defaults={'name': name},
                )
        elif model_name == 'subscription':
            for codename, name in [
                ('can_filter_subscriptions', 'Benutzer kann Abo filtern'),
                ('can_change_deactivated_subscriptions', 'Benutzer kann deaktivierte Abo ändern'),
                ('notified_on_depot_change', 'Wird bei Depot-Änderung informiert'),
                ('notified_on_subscription_creation', 'Wird bei Abo Erstellung informiert'),
                ('notified_on_subscription_cancellation', 'Wird bei Abo Kündigung informiert'),
            ]:
                Permission.objects.get_or_create(
                    codename=codename,
                    content_type=ct,
                    defaults={'name': name},
                )


def reverse_content_types(apps, schema_editor):
    """Reverse is a no-op - ContentTypes will be recreated by squashed migration."""
    pass


class RemoveBillable(Operation):
    """Custom operation to remove Billable polymorphic base from Share and Subscription."""

    reduces_to_sql = False
    elidable = True

    def state_forwards(self, app_label, state):
        """Modify the migration state to remove Billable inheritance."""
        share = state.models.get((app_label, 'share'))
        subscription = state.models.get((app_label, 'subscription'))

        # If Billable was never created (new squashed migration), this is a no-op
        if share and 'billable_ptr' not in share.fields:
            return
        if subscription and 'billable_ptr' not in subscription.fields:
            return

        # Remove Billable from bases
        if share:
            share.bases = tuple(
                b for b in share.bases
                if not (isinstance(b, str) and b.endswith('.billable'))
            )
        if subscription:
            subscription.bases = tuple(
                b for b in subscription.bases
                if not (isinstance(b, str) and b.endswith('.billable'))
            )

        # Replace billable_ptr with id
        if share and 'billable_ptr' in share.fields:
            del share.fields['billable_ptr']
            share.fields['id'] = models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
            )
        if subscription and 'billable_ptr' in subscription.fields:
            del subscription.fields['billable_ptr']
            subscription.fields['id'] = models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
            )

        # Remove polymorphic_ctype if present
        if share:
            share.fields.pop('polymorphic_ctype', None)
        if subscription:
            subscription.fields.pop('polymorphic_ctype', None)

        # Remove Billable model
        state.models.pop((app_label, 'billable'), None)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Apply database changes: rename columns and drop table."""
        connection = schema_editor.connection
        vendor = connection.vendor

        # SQLite is not supported in production - skip
        if vendor == 'sqlite':
            return

        # Check if Billable table exists - if not, this is a no-op (new squashed migration)
        with connection.cursor() as cursor:
            if vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'juntagrico_billable'
                """)
                exists = cursor.fetchone()[0] > 0
            else:
                # PostgreSQL
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = CURRENT_SCHEMA AND table_name = 'juntagrico_billable'
                """)
                exists = cursor.fetchone()[0] > 0
        if not exists:
            return

        if vendor == 'mysql':
            self._database_forwards_mysql(app_label, schema_editor, from_state)
        else:
            # PostgreSQL
            self._database_forwards_postgresql(app_label, schema_editor, from_state)

    def _database_forwards_mysql(self, app_label, schema_editor, from_state):
        """Handle MySQL: drop FK constraints, rename columns, drop table."""
        # Find ALL FK constraints referencing billable_ptr_id (both ON the table and FROM other tables)
        with schema_editor.connection.cursor() as cursor:
            # FKs ON share/subscription pointing TO billable (the parent link)
            cursor.execute("""
                SELECT TABLE_NAME, CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME IN ('juntagrico_share', 'juntagrico_subscription')
                  AND COLUMN_NAME = 'billable_ptr_id'
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            parent_fks = cursor.fetchall()

            # FKs FROM other tables pointing TO share.billable_ptr_id or subscription.billable_ptr_id
            cursor.execute("""
                SELECT kcu.TABLE_NAME, kcu.CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE AS kcu
                JOIN information_schema.TABLE_CONSTRAINTS AS tc
                  ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                  AND kcu.TABLE_SCHEMA = tc.TABLE_SCHEMA
                WHERE kcu.TABLE_SCHEMA = DATABASE()
                  AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
                  AND kcu.REFERENCED_TABLE_NAME IN ('juntagrico_share', 'juntagrico_subscription')
                  AND kcu.REFERENCED_COLUMN_NAME = 'billable_ptr_id'
            """)
            child_fks = cursor.fetchall()

        # Drop FK constraints ON share/subscription pointing to billable
        for table_name, fk_name in parent_fks:
            schema_editor.execute(
                f'ALTER TABLE `{table_name}` DROP FOREIGN KEY `{fk_name}`'
            )

        # Drop FK constraints FROM other tables pointing to share/subscription billable_ptr_id
        for table_name, fk_name in child_fks:
            schema_editor.execute(
                f'ALTER TABLE `{table_name}` DROP FOREIGN KEY `{fk_name}`'
            )

        # Rename columns and add AUTO_INCREMENT
        schema_editor.execute(
            'ALTER TABLE `juntagrico_share` CHANGE `billable_ptr_id` `id` BIGINT NOT NULL AUTO_INCREMENT'
        )
        schema_editor.execute(
            'ALTER TABLE `juntagrico_subscription` CHANGE `billable_ptr_id` `id` BIGINT NOT NULL AUTO_INCREMENT'
        )

        # Drop the Billable table
        schema_editor.execute('DROP TABLE IF EXISTS `juntagrico_billable`')

    def _database_forwards_postgresql(self, app_label, schema_editor, from_state):
        """Handle PostgreSQL: drop FK constraints, rename columns, add identity sequence, drop table."""
        # Dynamically find and drop FK constraints on share and subscription referencing billable
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                SELECT tc.table_name, tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_name IN ('juntagrico_share', 'juntagrico_subscription')
                  AND kcu.column_name = 'billable_ptr_id'
            """)
            fk_constraints = cursor.fetchall()

        for table_name, constraint_name in fk_constraints:
            schema_editor.execute(
                f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS "{constraint_name}"'
            )

        # Rename columns
        schema_editor.execute(
            'ALTER TABLE juntagrico_share RENAME COLUMN billable_ptr_id TO id'
        )
        schema_editor.execute(
            'ALTER TABLE juntagrico_subscription RENAME COLUMN billable_ptr_id TO id'
        )

        # Ensure id columns have an identity sequence and update sequence values to MAX(id)
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'juntagrico_share' AND column_name = 'id' AND is_identity = 'YES'
                    ) AND pg_get_serial_sequence('juntagrico_share', 'id') IS NULL THEN
                        ALTER TABLE juntagrico_share ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY;
                    END IF;
                    IF pg_get_serial_sequence('juntagrico_share', 'id') IS NOT NULL THEN
                        PERFORM setval(pg_get_serial_sequence('juntagrico_share', 'id'), COALESCE((SELECT MAX(id) FROM juntagrico_share), 1));
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'juntagrico_subscription' AND column_name = 'id' AND is_identity = 'YES'
                    ) AND pg_get_serial_sequence('juntagrico_subscription', 'id') IS NULL THEN
                        ALTER TABLE juntagrico_subscription ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY;
                    END IF;
                    IF pg_get_serial_sequence('juntagrico_subscription', 'id') IS NOT NULL THEN
                        PERFORM setval(pg_get_serial_sequence('juntagrico_subscription', 'id'), COALESCE((SELECT MAX(id) FROM juntagrico_subscription), 1));
                    END IF;
                END
                $$;
            """)

        # Drop the Billable table
        schema_editor.execute('DROP TABLE IF EXISTS juntagrico_billable')

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """Reverse database changes."""
        connection = schema_editor.connection
        vendor = connection.vendor

        # Recreate the Billable table
        schema_editor.execute(
            'CREATE TABLE juntagrico_billable (id bigint PRIMARY KEY, polymorphic_ctype_id integer)'
        )

        if vendor == 'mysql':
            schema_editor.execute(
                'ALTER TABLE `juntagrico_share` CHANGE `id` `billable_ptr_id` BIGINT NOT NULL'
            )
            schema_editor.execute(
                'ALTER TABLE `juntagrico_subscription` CHANGE `id` `billable_ptr_id` BIGINT NOT NULL'
            )
        else:
            # PostgreSQL
            schema_editor.execute(
                'ALTER TABLE juntagrico_share RENAME COLUMN id TO billable_ptr_id'
            )
            schema_editor.execute(
                'ALTER TABLE juntagrico_subscription RENAME COLUMN id TO billable_ptr_id'
            )

    def describe(self):
        return "Removes Billable polymorphic base class from Share and Subscription"


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('juntagrico', '0064_alter_specialroles_options'),
    ]

    operations = [
        RemoveBillable(),
        migrations.RunPython(ensure_content_types, reverse_content_types),
    ]
