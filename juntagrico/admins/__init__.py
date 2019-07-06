from django.contrib import admin

from juntagrico.util import addons


class BaseAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.inlines = self.inlines or []
        self.inlines.extend(addons.config.get_model_inlines(model))
        super().__init__(model, admin_site)
