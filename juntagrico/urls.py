from django.contrib.auth.views import LoginView
from django.urls import path

from juntagrico import views as juntagrico
from juntagrico import views_admin as juntagrico_admin
from juntagrico import views_create_subscription as juntagrico_cs
from juntagrico import views_iso20022 as juntagrico_iso20022
from juntagrico import views_subscription as juntagrico_subscription

urlpatterns = [
    # general juntagrico stuff
    path('home/', juntagrico.home, name='home'),  #
    path('my/password/', juntagrico.change_password, name='password'),  #
    path('my/password/restore', juntagrico.new_password, name='new-password'),  #

    path('jobs/', juntagrico.jobs, name='jobs'),  #
    path('jobs/all/', juntagrico.all_jobs, name='jobs-all'),  #
    path('job/<int:job_id>/', juntagrico.job, name='job'),  #

    path('my/membership/', juntagrico.profile, name='profile'),  #
    path('my/membership/cancel/', juntagrico.cancel_membership, name='cancel-membership'),  #

    path('contact/', juntagrico.contact, name='contact'),  #
    path('contact/member/<int:member_id>/', juntagrico.contact_member, name='contact-member'),  #

    path('my/assignments/', juntagrico.memberjobs, name='memberjobs'),  #

    path('depot/<int:depot_id>/', juntagrico.depot, name='depot'),  #
    path('deliveries/', juntagrico.deliveries, name='deliveries'),  #

    path('my/confirm/email/', juntagrico.send_confirm, name='send-confirm'),  #
    path('my/share/unpaid/', juntagrico.info_unpaid_shares, name='info-unpaid-shares'),  #

    path('cookies/', juntagrico.cookies, name='cookies'),  #
    path('logout/', juntagrico.logout_view, name='logout'),  #
    path('accounts/login/', LoginView.as_view(), name='login'),

    # area stuff
    path('areas/', juntagrico.areas, name='areas'),  #
    path('area/<int:area_id>/', juntagrico.show_area, name='area'),  #
    path('area/<int:area_id>/join/', juntagrico.area_join, name='area-join'),  #
    path('area/<int:area_id>/leave/', juntagrico.area_leave, name='area-leave'),  #

    # subscription related juntagrico stuff
    path('my/subscription/', juntagrico_subscription.subscription, name='sub-detail'),  #
    path('my/subscription/<int:subscription_id>/', juntagrico_subscription.subscription, name='sub-detail-id'),  #
    path('my/subscription/<int:subscription_id>/change/', juntagrico_subscription.subscription_change,
         name='sub-change'),  #
    path('my/subscription/<int:subscription_id>/change/depot/', juntagrico_subscription.depot_change,
         name='depot-change'),  #
    path('my/subscription/<int:subscription_id>/change/nickname/', juntagrico_subscription.change_nickname,
         name='nickname-change'),
    path('my/subscription/<int:subscription_id>/change/primary/', juntagrico_subscription.primary_change,
         name='primary-change'),  #
    path('my/subscription/<int:subscription_id>/change/parts/', juntagrico_subscription.size_change, name='size-change'),
    #
    path('my/subscription/<int:subscription_id>/change/extra/', juntagrico_subscription.extra_change,
         name='extra-change'),

    path('signup/', juntagrico_subscription.SignupView.as_view(), name='signup'),
    path('my/subscription/<int:subscription_id>/comember/add/', juntagrico_subscription.AddCoMemberView.as_view(), name='add-member'),
    path('my/subscription/confirm/<str:member_hash>/', juntagrico_subscription.confirm, name='confirm'),

    path('manage/subscription/<int:subscription_id>/activate/', juntagrico_subscription.activate_subscription,
         name='sub-activate'),  #
    path('manage/subscription/<int:subscription_id>/deactivate/', juntagrico_subscription.deactivate_subscription,
         name='sub-deactivate'),  #

    path('my/subscription/<int:subscription_id>/cancel/', juntagrico_subscription.cancel_subscription,
         name='sub-cancel'),
    path('my/subscription/<int:subscription_id>/leave/', juntagrico_subscription.leave_subscription,
         name='sub-leave'),  #

    path('manage/subscription/<int:subscription_id>/parts/apply/', juntagrico_subscription.activate_future_types,
         name='activate-future-types'),
    path('manage/subscription/extra/<int:extra_id>/activate/', juntagrico_subscription.activate_extra, name='extra-activate'),
    path('manage/subscription/extra/<int:extra_id>/deactivate/', juntagrico_subscription.deactivate_extra, name='extra-deactivate'),

    path('my/subscription/<int:subscription_id>/extra/<int:extra_id>/cancel/', juntagrico_subscription.cancel_extra,
         name='extra-cancel'),
    path('my/subscription/<int:subscription_id>/part/<int:part_id>/cancel/', juntagrico_subscription.cancel_part,
         name='part-cancel'),
    path('my/share/manage/', juntagrico_subscription.manage_shares, name='manage-shares'),  #
    path('my/share/<int:share_id>/cancel/', juntagrico_subscription.cancel_share, name='share-cancel'),

    path('manage/share/<int:share_id>/payout/', juntagrico_subscription.payout_share, name='share-payout'),

    path('create/subscription/parts/', juntagrico_cs.cs_select_subscription, name='cs-subscription'),
    path('create/subscription/selectdepot/', juntagrico_cs.cs_select_depot, name='cs-depot'),
    path('create/subscription/startdate/', juntagrico_cs.cs_select_start_date, name='cs-start'),
    path('create/subscription/addmembers/', juntagrico_cs.CSAddMemberView.as_view(), name='cs-co-members'),
    path('create/subscription/shares/', juntagrico_cs.CSSelectSharesView.as_view(), name='cs-shares'),
    path('create/subscription/summary/', juntagrico_cs.CSSummaryView.as_view(), name='cs-summary'),
    path('create/subscription/cancel/', juntagrico_cs.cs_cancel, name='cs-cancel'),
    path('welcome/', juntagrico_cs.cs_welcome, name='welcome'),
    path('welcome/with_sub/', juntagrico_cs.cs_welcome, {'with_sub': True}, name='welcome-with-sub'),

    # admin related juntagrico stuff
    path('manage/changedate/set/', juntagrico_admin.set_change_date, name='changedate-set'),  #
    path('manage/changedate/stop/', juntagrico_admin.unset_change_date, name='changedate-unset'),  #

    path('mails/send/depot/', juntagrico_admin.send_email_depot, name='mail-depot-send'),  #
    path('mails/send/area/', juntagrico_admin.send_email_area, name='mail-area-send'),  #
    path('mails/send/job/', juntagrico_admin.send_email_job, name='mail-job-send'),  #
    path('mails/send/', juntagrico_admin.send_email, name='mail-send'),  #
    path('mails/send/result/<int:numsent>/', juntagrico_admin.send_email_result, name='mail-result'),  #
    path('mails', juntagrico_admin.mails, name='mail'),  #
    path('mails/depot', juntagrico_admin.mails_depot, name='mail-depot'),  #
    path('mails/area', juntagrico_admin.mails_area, name='mail-area'),  #
    path('mails/job', juntagrico_admin.mails_job, name='mail-job'),  #

    path('filter/members/', juntagrico_admin.filters, name='filters'),  #
    path('filter/members/depot/<int:depot_id>/', juntagrico_admin.filters_depot, name='filter-depot'),  #
    path('filter/members/area/<int:area_id>/', juntagrico_admin.filters_area, name='filter-area'),  #
    path('filter/subscriptions/', juntagrico_admin.subscriptions, name='filter-subs'),  #
    path('filter/subscriptions/depot/<int:depot_id>/', juntagrico_admin.filter_subscriptions_depot,
         name='filter-subs-depot'),  #

    path('manage/subscriptions/future', juntagrico_admin.future, name='future'),  #

    path('mails/template/<int:template_id>/', juntagrico_admin.get_mail_template, name='mail-template'),  #

    path('manage/subscriptions/waiting/', juntagrico_admin.waitinglist, name='sub-mgmt-waitinglist'),  #
    path('manage/subscriptions/canceled/', juntagrico_admin.canceledlist, name='sub-mgmt-canceledlist'),  #
    path('manage/subscriptions/parts/', juntagrico_admin.typechangelist, name='sub-mgmt-changelist'),  #
    path('manage/subscriptions/inconsistencies/', juntagrico_admin.sub_inconsistencies, name='sub-mgmt-inconsistencies'),
    path('manage/subscriptions/extra/waiting/', juntagrico_admin.extra_waitinglist, name='sub-mgmt-extra-waitinglist'),  #
    path('manage/subscriptions/extra/canceled/', juntagrico_admin.extra_canceledlist, name='sub-mgmt-extra-canceledlist'),
    path('manage/shares/canceled/', juntagrico_admin.share_canceledlist, name='share-mgmt-canceledlist'),  #
    path('manage/member/canceled/', juntagrico_admin.member_canceledlist, name='member-mgmt-canceledlist'),
    path('manage/member/deactivate/<int:member_id>/', juntagrico_admin.deactivate_member, name='member-deactivate'),

    # lists
    path('list/depot/', juntagrico_admin.depotlist, name='lists-depotlist'),  #
    path('list/depotoverview/', juntagrico_admin.depot_overview, name='lists-depot-overview'),  #
    path('list/amountoverview/', juntagrico_admin.amount_overview, name='lists-depot-amountoverview'),  #

    # exports
    path('export/', juntagrico_admin.export, name='export'),  #
    path('export/members/filter/', juntagrico_admin.excel_export_members_filter, name='export-membersfilter'),  #
    path('export/members/', juntagrico_admin.excel_export_members, name='export-members'),  #
    path('export/shares/', juntagrico_admin.excel_export_shares, name='export-shares'),  #
    path('export/subscriptions/', juntagrico_admin.excel_export_subscriptions, name='export-subscriptions'),  #


    # iso20022
    path('api/share/iso20022/pain001/', juntagrico_iso20022.share_pain001, name='share-pain001'),  #
]
