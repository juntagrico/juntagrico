from django import forms
from django.contrib import admin

from juntagrico.entity.delivery import Delivery, DeliveryItem


class DeliveryCopyForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['delivery_date', 'subscription_size']
        widgets = {
            'delivery_date': admin.widgets.AdminDateWidget,
        }

    def __init__(self, *a, **k):
        super(DeliveryCopyForm, self).__init__(*a, **k)
        inst = k.pop('instance')

        self.fields['delivery_date'].initial = inst.delivery_date

    def save(self, commit=True):
        delivery_date = self.cleaned_data['delivery_date']
        subscription_size = self.cleaned_data['subscription_size']
        new_delivery = Delivery.objects.create(delivery_date=delivery_date, subscription_size=subscription_size)
        for item in self.instance.items.all():
            DeliveryItem.objects.create(delivery=new_delivery,
                                        name=item.name,
                                        amount=item.amount,
                                        comment=item.comment)
        return new_delivery

    def save_m2m(self):
        # HACK: the admin expects this method to exist
        pass
