from django.urls import path

from juntagrico.views import subscription, manage

"""
Include these urls first to keep old links alive
"""

urlpatterns = [
    # Changed in 1.6
    path('my/subscription/detail/', subscription.landing, name='sub-detail'),
    path('my/subscription/detail/<int:subscription_id>/', subscription.single, name='sub-detail-id'),
    path('my/subscription/change/size/<int:subscription_id>/', subscription.single, name='size-change'),

    # Changed in 1.7
    path('my/subscriptions', manage.SubscriptionView.as_view(), name='filter-subs'),
    path('my/sub/inconsistencies', manage.subscription_inconsistencies, name='sub-mgmt-inconsistencies'),
    # /manage/member
    path('my/member/canceledlist', manage.MemberCanceledView.as_view(), name='member-mgmt-canceledlist'),
    path('my/member/deactivate/<int:member_id>/', manage.member_deactivate, name='member-deactivate'),
    path('my/filters', manage.MemberView.as_view(), name='filters'),
    path('my/filters/active', manage.MemberActiveView.as_view(), name='filters-active'),
    # /manage/assignments
    path('my/assignments', manage.AssignmentsView.as_view(), name='filter-assignments'),
    # /manage/share
    path('my/share/canceledlist', manage.ShareCanceledView.as_view(), name='share-mgmt-canceledlist'),
    path('my/payout/share/<int:share_id>/', manage.share_payout, name='share-payout'),
    # /manage/depot
    path('my/filters/depot/<int:depot_id>/', manage.DepotSubscriptionView.as_view(), name='filter-depot'),
    path('my/subscriptions/depot/<int:depot_id>/', manage.DepotSubscriptionView.as_view(),
         name='filter-subs-depot'),
    # /manage/area
    path('my/filters/area/<int:area_id>/', manage.AreaMemberView.as_view(), name='filter-area'),
]
