from django.urls import path

from juntagrico.views import subscription

"""
Include these urls first to keep old links alive
"""

urlpatterns = [
    path('my/subscription/detail/', subscription.landing, name='sub-detail'),
    path('my/subscription/detail/<int:subscription_id>/', subscription.single, name='sub-detail-id'),
    path('my/subscription/change/size/<int:subscription_id>/', subscription.single, name='size-change'),
]
