from django.db.models import F
from django.shortcuts import render

from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionBundle


def overview(request):
    return render(request, 'juntagrico/config/overview.html', {
        'products': SubscriptionProduct.objects.all(),
        'bundles': SubscriptionBundle.objects.order_by(F('category__sort_order').asc(nulls_last=True)),
    })
