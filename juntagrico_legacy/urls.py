from django.urls import path

from juntagrico_legacy import views

urlpatterns = [
    path('my/waitinglist', views.waitinglist, name='sub-mgmt-waitinglist'),
    path('my/canceledlist', views.canceledlist, name='sub-mgmt-canceledlist'),
    path('manage/subscription/part/waitinglist', views.part_waitinglist, name='sub-mgmt-part-waitinglist'),
    path('manage/subscription/part/canceledlist', views.part_canceledlist,
         name='sub-mgmt-part-canceledlist'),
    # /manage/subscription/extra
    path('my/extra/waitinglist', views.extra_waitinglist, name='sub-mgmt-extra-waitinglist'),
    path('my/extra/canceledlist', views.extra_canceledlist, name='sub-mgmt-extra-canceledlist'),

    # /export
    path('my/export', views.export, name='export'),
    path('my/export/membersfilter', views.excel_export_members_filter, name='export-membersfilter'),
    path('my/export/members', views.excel_export_members, name='export-members'),
    path('my/export/shares', views.excel_export_shares, name='export-shares'),
    path('my/export/subscriptions', views.excel_export_subscriptions, name='export-subscriptions'),
]
