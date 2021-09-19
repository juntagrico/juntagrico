from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.forms.delivery_copy_form import DeliveryCopyForm
from juntagrico.admins.inlines.delivery_inline import DeliveryInline


class DeliveryAdmin(BaseAdmin):
    list_display = ('__str__', 'delivery_date', 'subscription_size')
    ordering = ('-delivery_date', 'subscription_size')
    actions = ['copy_delivery']
    search_fields = ['delivery_date', 'subscription_size']
    inlines = [DeliveryInline]
    save_as = True

    @admin.action(description=_('Lieferung kopieren...'))
    @single_element_action('Genau 1 Lieferung auswählen!')
    def copy_delivery(self, request, queryset):
        inst, = queryset.all()
        return HttpResponseRedirect('copy_delivery/%s/' % inst.id)

    def get_form(self, request, obj=None, **kwds):
        if 'copy_delivery' in request.path:
            return DeliveryCopyForm
        return super().get_form(request, obj, **kwds)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^copy_delivery/(?P<deliveryid>.*?)/$',
                self.admin_site.admin_view(self.copy_delivery_view))
        ]
        return my_urls + urls

    def copy_delivery_view(self, request, deliveryid):
        # HUGE HACK: modify admin properties just for this view
        tmp_readonly = self.readonly_fields
        tmp_inlines = self.inlines
        self.readonly_fields = []
        self.inlines = []
        res = self.change_view(request, deliveryid, extra_context={
            'title': 'Copy delivery'})
        self.readonly_fields = tmp_readonly
        self.inlines = tmp_inlines
        return res
