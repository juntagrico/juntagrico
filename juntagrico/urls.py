from django.contrib.auth.views import LoginView
from django.urls import path

from juntagrico import views as juntagrico
from juntagrico import views_admin as juntagrico_admin
from juntagrico import views_create_subscription as juntagrico_cs
from juntagrico import views_iso20022 as juntagrico_iso20022
from juntagrico import views_subscription as juntagrico_subscription

urlpatterns = [
    # general juntagrico stuff
    path('my/home', juntagrico.home, name='home'),  #
    path('my/password', juntagrico.change_password, name='password'),
    path('my/newpassword', juntagrico.new_password, name='new-password'),
    path('my/jobs', juntagrico.jobs, name='jobs'),  #
    path('my/jobs/all', juntagrico.all_jobs, name='jobs-all'),  #
    path('my/jobs/<int:job_id>/', juntagrico.job, name='job'),  #
    path('my/profile', juntagrico.profile, name='profile'),  #
    path('my/cancel/membership', juntagrico.cancel_membership, name='cancel-membership'),  #
    path('my/contact', juntagrico.contact, name='contact'),  #
    path('my/contact/member/<int:member_id>/<int:job_id>/', juntagrico.contact_member, name='contact-member'),  #
    path('my/memberjobs', juntagrico.memberjobs, name='memberjobs'),  #
    path('my/depot/<int:depot_id>/', juntagrico.depot, name='depot'),  #
    path('my/deliveries', juntagrico.deliveries, name='deliveries'),  #
    path('my/sendconfirm', juntagrico.send_confirm, name='send-confirm'),
    path('my/info/unpaidshares', juntagrico.info_unpaid_shares, name='info-unpaid-shares'),  #
    path('my/cookies', juntagrico.cookies, name='cookies'),  #
    path('logout/', juntagrico.logout_view, name='logout'),
    path('accounts/login/', LoginView.as_view(), name='login'),

    # area stuff
    path('my/areas', juntagrico.areas, name='areas'),  #
    path('my/area/<int:area_id>/', juntagrico.show_area, name='area'),  #
    path('my/area/<int:area_id>/join', juntagrico.area_join, name='area-join'),  #
    path('my/area/<int:area_id>/leave', juntagrico.area_leave, name='area-leave'),  #

    # subscription related juntagrico stuff
    path('my/subscription/detail/', juntagrico_subscription.subscription, name='sub-detail'),  #
    path('my/subscription/detail/<int:subscription_id>/', juntagrico_subscription.subscription, name='sub-detail-id'),  #
    path('my/subscription/change/overview/<int:subscription_id>/', juntagrico_subscription.subscription_change,
         name='sub-change'),  #
    path('my/subscription/change/depot/<int:subscription_id>/', juntagrico_subscription.depot_change,
         name='depot-change'),  #
    path('my/subscription/change/primary/<int:subscription_id>/', juntagrico_subscription.primary_change,
         name='primary-change'),  #
    path('my/subscription/change/size/<int:subscription_id>/', juntagrico_subscription.size_change, name='size-change'),
    #
    path('my/subscription/change/extra/<int:subscription_id>/', juntagrico_subscription.extra_change,
         name='extra-change'),
    path('my/signup/', juntagrico_subscription.SignupView.as_view(), name='signup'),
    path('my/cosubmember/<int:subscription_id>/', juntagrico_subscription.AddCoMemberView.as_view(), name='add-member'),
    path('my/confirm/<str:member_hash>/', juntagrico_subscription.confirm, name='confirm'),
    path('my/subscription/activate/<int:subscription_id>/', juntagrico_subscription.activate_subscription,
         name='sub-activate'),  #
    path('my/subscription/deactivate/<int:subscription_id>/', juntagrico_subscription.deactivate_subscription,
         name='sub-deactivate'),  #
    path('my/subscription/cancel/<int:subscription_id>/', juntagrico_subscription.cancel_subscription,
         name='sub-cancel'),
    path('my/subscription/leave/<int:subscription_id>/', juntagrico_subscription.leave_subscription,
         name='sub-leave'),  #
    path('my/type/change/<int:subscription_id>/', juntagrico_subscription.activate_future_types,
         name='activate-future-types'),
    path('my/extra/activate/<int:extra_id>/', juntagrico_subscription.activate_extra, name='extra-activate'),
    path('my/extra/deactivate/<int:extra_id>/', juntagrico_subscription.deactivate_extra, name='extra-deactivate'),
    path('my/extra/cancel/<int:extra_id>/<int:subscription_id>/', juntagrico_subscription.cancel_extra,
         name='extra-cancel'),
    path('my/order/share/', juntagrico_subscription.order_shares, name='share-order'),
    path('my/order/share/success', juntagrico_subscription.order_shares_success, name='share-order-success'),
    path('my/payout/share/<int:share_id>/', juntagrico_subscription.payout_share, name='share-payout'),
    path('my/create/subscription/', juntagrico_cs.cs_select_subscription, name='cs-subscription'),
    path('my/create/subscription/selectdepot/', juntagrico_cs.cs_select_depot, name='cs-depot'),
    path('my/create/subscription/start/', juntagrico_cs.cs_select_start_date, name='cs-start'),
    path('my/create/subscription/addmembers/', juntagrico_cs.CSAddMemberView.as_view(), name='cs-co-members'),
    path('my/create/subscription/shares/', juntagrico_cs.CSSelectSharesView.as_view(), name='cs-shares'),
    path('my/create/subscription/summary/', juntagrico_cs.CSSummaryView.as_view(), name='cs-summary'),
    path('my/create/subscription/cancel/', juntagrico_cs.cs_finish, {'cancelled': True}, name='cs-cancel'),
    path('my/welcome/', juntagrico_cs.cs_welcome, name='welcome'),

    # admin related juntagrico stuff
    path('my/changedate', juntagrico_admin.set_change_date, name='changedate-set'),
    path('my/changedate/stop', juntagrico_admin.unset_change_date, name='changedate-unset'),
    path('my/mails/send/depot', juntagrico_admin.send_email_depot, name='mail-depot-send'),
    path('my/mails/send/area', juntagrico_admin.send_email_area, name='mail-area-send'),
    path('my/mails/send', juntagrico_admin.send_email, name='mail-send'),  #
    path('my/mails/send/result/<int:numsent>/', juntagrico_admin.send_email_result, name='mail-result'),  #
    path('my/mails', juntagrico_admin.mails, name='mail'),  #
    path('my/mails/depot', juntagrico_admin.mails_depot, name='mail-depot'),
    path('my/mails/area', juntagrico_admin.mails_area, name='mail-area'),
    path('my/filters', juntagrico_admin.filters, name='filters'),
    path('my/filters/depot/<int:depot_id>/', juntagrico_admin.filters_depot, name='filter-depot'),
    path('my/filters/area/<int:area_id>/', juntagrico_admin.filters_area, name='filter-area'),
    path('my/subscriptions', juntagrico_admin.subscriptions, name='filter-subs'),  #
    path('my/subscriptions/depot/<int:depot_id>/', juntagrico_admin.filter_subscriptions_depot,
         name='filter-subs-depot'),  #
    path('my/future', juntagrico_admin.future, name='future'),
    path('my/export', juntagrico_admin.export, name='export'),  #
    path('my/export/membersfilter', juntagrico_admin.excel_export_members_filter, name='export-membersfilter'),  #
    path('my/export/members', juntagrico_admin.excel_export_members, name='export-members'),  #
    path('my/export/shares', juntagrico_admin.excel_export_shares, name='export-shares'),  #
    path('my/mailtemplate/<int:template_id>/', juntagrico_admin.get_mail_template, name='mail-template'),
    path('my/waitinglist', juntagrico_admin.waitinglist, name='sub-mgmt-waitinglist'),  #
    path('my/canceledlist', juntagrico_admin.canceledlist, name='sub-mgmt-canceledlist'),  #
    path('my/typechangedlist', juntagrico_admin.typechangelist, name='sub-mgmt-changelist'),  #
    path('my/extra/waitinglist', juntagrico_admin.extra_waitinglist, name='sub-mgmt-extra-waitinglist'),  #
    path('my/extra/canceledlist', juntagrico_admin.extra_canceledlist, name='sub-mgmt-extra-canceledlist'),  #
    path('my/share/canceledlist', juntagrico_admin.share_canceledlist, name='share-mgmt-canceledlist'),  #
    path('my/member/canceledlist', juntagrico_admin.member_canceledlist, name='member-mgmt-canceledlist'),
    path('my/pdf/depotlist', juntagrico_admin.depotlist, name='lists-depotlist'),
    path('my/pdf/depotoverview', juntagrico_admin.depot_overview, name='lists-depot-overview'),
    path('my/pdf/amountoverview', juntagrico_admin.amount_overview, name='lists-depot-amountoverview'),
    path('my/member/deactivate/<int:member_id>/', juntagrico_admin.deactivate_member, name='member-deactivate'),

    path('my/iso20022/shares/pain001', juntagrico_iso20022.share_pain001, name='share-pain001'),  #
]
