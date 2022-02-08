from django.conf import settings
from django.contrib import admin
from django.db.models import TextField
from djrichtextfield.widgets import RichTextWidget

from juntagrico.util import addons


class BaseAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.inlines = self.inlines or []
        self.inlines.extend(addons.config.get_model_inlines(model))
        super().__init__(model, admin_site)


class RichTextAdmin(BaseAdmin):

    def __init__(self, model, admin_site):
        if 'djrichtextfield' in settings.INSTALLED_APPS and hasattr(settings, 'DJRICHTEXTFIELD_CONFIG'):
            self.formfield_overrides = self.formfield_overrides or {}
            self.formfield_overrides.update({TextField: {'widget': RichTextWidget}})
        super().__init__(model, admin_site)
