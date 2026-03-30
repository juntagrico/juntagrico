# Source - https://stackoverflow.com/a/73878251
# Posted by kdb
# Retrieved 2026-03-18, License - CC BY-SA 4.0
# extended for updating permission names

from typing import Set, Tuple, Dict

import django.apps

# noinspection PyProtectedMember
from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS


class Command(BaseCommand):
    help = "Update or remove custom permissions that have changed definition in models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=f'Specifies the database to use. Default is "{DEFAULT_DB_ALIAS}".',
        )
        parser.add_argument(
            "--dry",
            action="store_true",
            help="Do a dry run not actually updating any permissions",
        )

    def handle(self, *args, **options) -> str:
        using = options["database"]

        # This will hold the permissions that models have defined,
        # i.e. default permissions plus additional custom permissions:
        #       (content_type.pk, codename)
        defined_perms: Dict[Tuple[int, str], str] = {}

        for model in django.apps.apps.get_models():
            ctype = ContentType.objects.db_manager(using).get_for_model(
                model, for_concrete_model=False
            )

            # noinspection PyProtectedMember
            for (codename, name) in _get_all_permissions(model._meta):
                defined_perms[(ctype.id, codename)] = name

        # All permissions in current database (including stale ones)
        all_perms = Permission.objects.using(using).all()

        stale_perm_pks: Set[int] = set()
        renamed_perms: Dict[int, str] = {}
        for perm in all_perms:
            this_perm = (perm.content_type.pk, perm.codename)
            if this_perm not in defined_perms:
                stale_perm_pks.add(perm.pk)
                self.stdout.write(f"Delete permission: {perm}")
            elif perm.name != defined_perms[this_perm]:
                renamed_perms[perm.pk] = defined_perms[this_perm]
                self.stdout.write(f"Rename permission: {perm} -> {defined_perms[this_perm]}")

        # Delete all stale permissions
        if options["dry"]:
            result = f"DRY RUN: {len(stale_perm_pks)} permissions NOT deleted, {len(renamed_perms)} permissions NOT renamed"
        else:
            result = ""
            if stale_perm_pks:
                Permission.objects.filter(pk__in=stale_perm_pks).delete()
            result += f"{len(stale_perm_pks)} stale permissions deleted"
            if renamed_perms:
                for perm in Permission.objects.filter(pk__in=renamed_perms):
                    perm.name = renamed_perms[perm.pk]
                    perm.save()
                result += f"{len(renamed_perms)} permissions renamed"

        return result
