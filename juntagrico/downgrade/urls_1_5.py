from django.urls import path

from juntagrico import views_subscription as juntagrico_subscription

"""
Include these urls last to revert to interface from juntagrico 1.5.
"""

urlpatterns = [
    path('my/subscription/detail/', juntagrico_subscription.subscription, name='subscription-landing'),
    path('my/subscription/detail/<int:subscription_id>/', juntagrico_subscription.subscription, name='subscription-single'),
    path('my/subscription/change/size/<int:subscription_id>/', juntagrico_subscription.size_change, name='size-change'),
]
