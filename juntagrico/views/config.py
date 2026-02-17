from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.shortcuts import render

from juntagrico.config import Config
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionBundle, SubscriptionCategory


@staff_member_required
def overview(request):
    return render(request, 'juntagrico/config/overview.html', {
        'products': SubscriptionProduct.objects.all(),
        'categories': SubscriptionCategory.objects.all(),
        'bundles': SubscriptionBundle.objects.order_by(F('category__sort_order').asc(nulls_last=True), 'sort_order'),
        'hours_used': Config.assignment_unit() == 'HOURS',
    })
