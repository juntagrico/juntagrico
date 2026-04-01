# https://forum.djangoproject.com/t/duplicate-permissions-created-on-model-rename/22740/4
from typing import TYPE_CHECKING, Any

from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS, migrations, router


if TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    from django.db.migrations.state import StateApps


class RenamePermissions(migrations.RunPython):
    """
    Rename the auto-generated permissions of a model. Automatically appended _after_
    every `RenameModel` operation.
    """

    def __init__(self, app_label: str, old_model: str, new_model: str) -> None:
        self.app_label = app_label
        self.old_model = old_model
        self.new_model = new_model
        super().__init__(self._forwards, self._backwards)

    def _rename_permissions(
        self,
        apps: "StateApps",
        schema_editor: "BaseDatabaseSchemaEditor",
        old_model: str,
        new_model: str,
    ) -> None:
        Permission = apps.get_model("auth", "Permission")
        db = schema_editor.connection.alias
        if not router.allow_migrate_model(db, Permission):
            return

        ContentType = apps.get_model("contenttypes", "ContentType")
        NewModel = apps.get_app_config(self.app_label).get_model(self.new_model)

        # Depending on the order in which the current app was installed compared to
        # contenttypes, the content type might or might not have been renamed already.
        # Just to make sure, we're trying both model names.
        try:
            content_type = ContentType.objects.get(
                app_label=self.app_label, model=self.old_model
            )
        except ContentType.DoesNotExist:
            content_type = ContentType.objects.get(
                app_label=self.app_label, model=self.new_model
            )

        for action in NewModel._meta.default_permissions:
            try:
                permission = Permission.objects.using(db).get(
                    content_type=content_type, codename=f"{action}_{old_model}"
                )
                permission.codename = f"{action}_{new_model}"
                permission.name = f"Can {action} {NewModel._meta.verbose_name_raw}"
                permission.save()
            except Permission.DoesNotExist:
                # If the CreateModel and RenameModel are run in the same migration,
                # the permissions will only be created at the end and will therefore
                # not exist yet.
                pass

    def _forwards(
        self, apps: "StateApps", schema_editor: "BaseDatabaseSchemaEditor", /
    ) -> None:
        self._rename_permissions(apps, schema_editor, self.old_model, self.new_model)

    def _backwards(
        self, apps: "StateApps", schema_editor: "BaseDatabaseSchemaEditor", /
    ) -> None:
        self._rename_permissions(apps, schema_editor, self.new_model, self.old_model)


def inject_rename_permissions(
    plan: list[tuple[migrations.Migration, bool]] | None = None,
    apps: "Apps" = global_apps,
    using: str = DEFAULT_DB_ALIAS,
    **kwargs: Any,
) -> None:
    if plan is None:
        return

    # Determine whether or not the Permission model is available.
    try:
        Permission = apps.get_model("auth", "Permission")
    except LookupError:
        available = False
    else:
        if not router.allow_migrate_model(using, Permission):
            return
        available = True

    for migration, backward in plan:
        if (migration.app_label, migration.name) == ("auth", "0001_initial"):
            # The Permission model is created by the (auth, 0001_initial)
            # migration. Once it has run, the model is available.
            if backward:
                break
            else:
                available = True
                continue
        if not available:
            continue

        inserts = []
        for index, operation in enumerate(migration.operations):
            if isinstance(operation, migrations.RenameModel):
                operation = RenamePermissions(
                    migration.app_label,
                    operation.old_name_lower,
                    operation.new_name_lower,
                )
                inserts.append((index + 1, operation))
        for inserted, (index, operation) in enumerate(inserts):
            migration.operations.insert(inserted + index, operation)  # type: ignore[attr-defined]
