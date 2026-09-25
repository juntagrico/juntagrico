from django.apps import apps
from django.db.models import Q, CharField, TextField
from django.contrib import admin


def full_text_search(
    query_string,
    exclude_models=None,
    exclude_fields=None,
):
    """
    Args:
        query_string: Text to search for
        exclude_models: List of app.model names to skip (e.g., ['auth.Permission'])
        exclude_fields: List of field names to skip (e.g., ['password'])
    """
    results = []
    exclude_models = exclude_models or ['auth.Permission', 'contenttypes.ContentType', 'sessions.Session']
    exclude_fields = exclude_fields or ['password', 'token', 'secret']

    for model in apps.get_models():
        # Skip excluded models
        app_label = model._meta.app_label
        if f'{app_label}.{model.__name__}' in exclude_models:
            continue

        # Find searchable text fields
        text_fields = [
            field.name
            for field in model._meta.get_fields()
            if isinstance(field, (CharField, TextField))
            and field.name not in exclude_fields
        ]

        if not text_fields:
            continue

        # Build query
        q_objects = Q()
        for field_name in text_fields:
            q_objects |= Q(**{f'{field_name}__icontains': query_string})

        try:
            matches = model.objects.filter(q_objects)
            if matches.exists():
                # Check if model is registered in admin
                admin_url = None
                if model in admin.site._registry:
                    admin_url = f'admin:{app_label}_{model._meta.model_name}_change'

                results.append(
                    {
                        'sort_order': ('!!!' if app_label.startswith('juntagrico') else '') + app_label,
                        'model': model,
                        'model_name': model._meta.verbose_name,
                        'app': app_label,
                        'matches': matches,
                        'count': matches.count(),
                        'searched_fields': text_fields,
                        'admin_url_template': admin_url,
                    }
                )
        except Exception:
            pass

    return sorted(results, key=lambda x: x['sort_order'])
