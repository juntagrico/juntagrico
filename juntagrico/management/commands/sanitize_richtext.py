from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db.models import TextField

from juntagrico.defaults import sanitize_html


RICH_TEXT_FIELDS = [
    'juntagrico.Location.description',
    'juntagrico.ActivityArea.description',
    'juntagrico.JobType.description',
    'juntagrico.RecuringJob.additional_description',
    'juntagrico.OneTimeJob.description',
    'juntagrico.Tour.description',
    'juntagrico.Depot.description',
    'juntagrico.Depot.access_information',
    'juntagrico.SubscriptionProduct.description',
    'juntagrico.SubscriptionCategory.description',
    'juntagrico.SubscriptionBundle.description',
    'juntagrico.SubscriptionType.description',
]


class Command(BaseCommand):
    help = 'Sanitize selected TextField values as HTML.'

    def add_arguments(self, parser):
        parser.add_argument(
            'fields',
            nargs='*',
            help='Fields in app_label.ModelName.field_name format. '
                 'Default to all relevant juntagrico rich text fields',
        )
        parser.add_argument('--batch-size', type=int, default=500)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        fields = options['fields'] or RICH_TEXT_FIELDS
        for field_spec in fields:
            try:
                app_label, model_name, field_name = field_spec.split('.', 2)
                model = apps.get_model(app_label, model_name)
                field = model._meta.get_field(field_name)
            except (ValueError, LookupError) as exc:
                raise CommandError(
                    f'Invalid field {field_spec!r}; expected '
                    'app_label.ModelName.field_name.'
                ) from exc

            if not isinstance(field, TextField) or not field.concrete:
                raise CommandError(f'{field_spec} is not a concrete TextField.')

            updated = 0
            queryset = (
                model._default_manager.exclude(**{f'{field.attname}__isnull': True})
                .exclude(**{field.attname: ''})
                .only(model._meta.pk.name, field.attname)
            )

            for obj in queryset.iterator(chunk_size=options['batch_size']):
                original = getattr(obj, field.attname)
                cleaned = sanitize_html(original)

                if cleaned != original:
                    updated += 1
                    if not options['dry_run']:
                        model._default_manager.filter(pk=obj.pk).update(
                            **{field.attname: cleaned}
                        )

            action = 'would update' if options['dry_run'] else 'updated'
            self.stdout.write(f'{field_spec}: {updated} record(s) {action}.')
