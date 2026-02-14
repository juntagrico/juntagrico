from django.urls import path

from juntagrico_legacy import views

"""
Include these urls last to revert to interface from juntagrico 1.5.
"""

urlpatterns = [
    path('my/subscription/detail/', views.subscription, name='subscription-landing'),
    path('my/subscription/detail/<int:subscription_id>/', views.subscription, name='subscription-single'),
    path('my/subscription/change/size/<int:subscription_id>/', views.size_change, name='size-change'),
]
