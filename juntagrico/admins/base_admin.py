from django.contrib import admin

from juntagrico.entity.billing import ExtraSubBillingPeriod
from juntagrico.entity.extrasubs import ExtraSubscriptionCategory
from juntagrico.entity.jobs import JobExtra, JobExtraType
from juntagrico.entity.subtypes import SubscriptionProduct
from juntagrico.util import addons


@admin.register(JobExtra, JobExtraType, ExtraSubBillingPeriod, ExtraSubscriptionCategory, SubscriptionProduct)
class BaseAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.inlines = self.inlines or []
        self.inlines.extend(addons.config.get_model_inlines(model))
        super().__init__(model, admin_site)
