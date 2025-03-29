from django.contrib.auth import views as auth_views
from django.urls import path

from juntagrico import views as juntagrico
from juntagrico import views_admin as juntagrico_admin
from juntagrico import views_create_subscription as juntagrico_cs
from juntagrico import views_iso20022 as juntagrico_iso20022
from juntagrico import views_subscription as juntagrico_subscription
from juntagrico.config import Config
from juntagrico.util.auth import JuntagricoLoginView, JuntagricoPasswordResetForm
from juntagrico.views import subscription, manage, email, job, api
from juntagrico.views_admin import ShiftTimeFormView

# GUIDELINES for adding urls
# 1. Add the url to the section that matches best and start the url as the section title says
# 2. Use "my" only in the corresponding sections
# 3. IDs go directly after the name of the entity they belong to e.g. manage/subscription/extra/{extra-id}/activate

urlpatterns = [
    # /signup
    path('my/signup/', juntagrico_subscription.SignupView.as_view(), name='signup'),
    path('my/create/subscription/', juntagrico_cs.cs_select_subscription, name='cs-subscription'),
    path('my/create/subscription/selectdepot/', juntagrico_cs.cs_select_depot, name='cs-depot'),
    path('my/create/subscription/start/', juntagrico_cs.cs_select_start_date, name='cs-start'),
    path('my/create/subscription/addmembers/', juntagrico_cs.CSAddMemberView.as_view(), name='cs-co-members'),
    path('my/create/subscription/shares/', juntagrico_cs.CSSelectSharesView.as_view(), name='cs-shares'),
    path('my/create/subscription/summary/', juntagrico_cs.CSSummaryView.as_view(), name='cs-summary'),
    path('my/create/subscription/cancel/', juntagrico_cs.cs_cancel, name='cs-cancel'),
    path('my/welcome/', juntagrico_cs.cs_welcome, name='welcome'),
    path('my/welcome/with_sub', juntagrico_cs.cs_welcome, {'with_sub': True}, name='welcome-with-sub'),
    path('my/confirm/<str:member_hash>/', juntagrico_subscription.confirm, name='confirm'),

    # login/
    path('accounts/login/', JuntagricoLoginView.as_view(), name='login'),
    # logout/
    path('logout/', juntagrico.logout_view, name='logout'),

    # /accounts (password reset)
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form_cust.html',
                                                                          email_template_name=Config.emails('password'),
                                                                          form_class=JuntagricoPasswordResetForm,
                                                                          from_email=Config.contacts('technical')), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done_cust.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm_cust.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete_cust.html'), name='password_reset_complete'),

    # /home
    path('my/home', juntagrico.home, name='home'),  # for backwards compatibility since 1.6.0
    path('', juntagrico.home, name='home'),

    # /my (personal stuff)
    # /my/password
    path('my/password', juntagrico.change_password, name='password'),
    # my/email
    path('my/sendconfirm', juntagrico.send_confirm, name='send-confirm'),
    # /my/membership
    path('my/profile', juntagrico.profile, name='profile'),
    path('my/cancel/membership', juntagrico.cancel_membership, name='cancel-membership'),
    # /my/share
    path('my/share/manage/', juntagrico_subscription.manage_shares, name='manage-shares'),
    path('my/share/certificate', juntagrico_subscription.share_certificate, name='share-certificate'),
    path('my/share/cancel/<int:share_id>/', juntagrico_subscription.cancel_share, name='share-cancel'),
    path('my/info/unpaidshares', juntagrico.info_unpaid_shares, name='info-unpaid-shares'),
    # /my/subscription
    path('my/subscription/', subscription.landing, name='subscription-landing'),
    # /my/subscription/{id}
    path('my/subscription/<int:subscription_id>/', subscription.single, name='subscription-single'),
    path('my/subscription/<int:subscription_id>/', subscription.single, name='size-change'),  # compatibility
    path('my/subscription/<int:subscription_id>/order/', subscription.part_order, name='part-order'),
    path('my/subscription/<int:subscription_id>/order/extra/', subscription.part_order, {'extra': True}, name='extra-order'),
    path('my/subscription/change/overview/<int:subscription_id>/', juntagrico_subscription.subscription_change,
         name='sub-change'),
    path('my/subscription/change/depot/<int:subscription_id>/', juntagrico_subscription.depot_change,
         name='depot-change'),
    path('my/subscription/change/nickname/<int:subscription_id>/', juntagrico_subscription.change_nickname,
         name='nickname-change'),
    path('my/subscription/change/primary/<int:subscription_id>/', juntagrico_subscription.primary_change,
         name='primary-change'),
    path('my/cosubmember/<int:subscription_id>/', juntagrico_subscription.AddCoMemberView.as_view(), name='add-member'),
    path('my/subscription/cancel/<int:subscription_id>/', juntagrico_subscription.cancel_subscription,
         name='sub-cancel'),
    path('my/subscription/leave/<int:subscription_id>/', juntagrico_subscription.leave_subscription,
         name='sub-leave'),
    # /my/subscription/extra/{id}
    path('my/subscription/change/extra/<int:subscription_id>/', juntagrico_subscription.extra_change,
         name='extra-change'),
    # /my/subscription/part/{id}
    path('my/subscription/part/<int:part_id>/change', juntagrico_subscription.part_change, name='part-change'),
    path('my/subpart/cancel/<int:part_id>/<int:subscription_id>/', juntagrico_subscription.cancel_part,
         name='part-cancel'),
    # /my/assignments
    path('my/memberjobs', job.memberjobs, name='memberjobs'),

    # /job
    path('my/jobs', job.jobs, name='jobs'),
    path('my/jobs/all', job.all_jobs, name='jobs-all'),
    path('job/list/data', job.list_data, name='jobs-list-data'),
    path('my/jobs/<int:job_id>/', job.job, name='job'),

    # /assignment
    path('assignment/<int:job_id>/<int:member_id>/edit', job.edit_assignment, name='assignment-edit'),

    # /area
    path('my/areas', juntagrico.areas, name='areas'),
    path('my/area/<int:area_id>/', juntagrico.show_area, name='area'),
    path('my/area/<int:area_id>/join', juntagrico.area_join, name='area-join'),
    path('my/area/<int:area_id>/leave', juntagrico.area_leave, name='area-leave'),

    # /depot
    path('my/depot/<int:depot_id>/', juntagrico.depot, name='depot'),
    path('my/depot/', juntagrico.depot_landing, name='depot-landing'),

    # /deliveries
    path('my/deliveries', juntagrico.deliveries, name='deliveries'),

    # /contact
    path('my/contact', juntagrico.contact, name='contact'),
    path('my/contact/member/<int:member_id>/', juntagrico.contact_member, name='contact-member'),

    # /cookies
    path('my/cookies', juntagrico.cookies, name='cookies'),

    # /manage (administration stuff)
    # /manage/changedate
    path('my/changedate', juntagrico_admin.set_change_date, name='changedate-set'),
    path('my/changedate/stop', juntagrico_admin.unset_change_date, name='changedate-unset'),
    # /manage/subscription
    path('manage/subscription/recent', manage.SubscriptionRecentView.as_view(), name='manage-sub-recent'),
    path('manage/subscription', manage.SubscriptionView.as_view(), name='manage-subscription'),
    path('manage/subscription/pending', manage.SubscriptionPendingView.as_view(), name='manage-sub-pending'),
    path('my/waitinglist', juntagrico_admin.waitinglist, name='sub-mgmt-waitinglist'),
    path('my/canceledlist', juntagrico_admin.canceledlist, name='sub-mgmt-canceledlist'),
    path('my/future', juntagrico_admin.future, name='future'),
    path('manage/subscription/inconsistencies', manage.subscription_inconsistencies,
         name='manage-subscription-inconsistencies'),
    path('my/subscription/activate/<int:subscription_id>/', juntagrico_subscription.activate_subscription,
         name='sub-activate'),
    path('my/subscription/deactivate/<int:subscription_id>/', juntagrico_subscription.deactivate_subscription,
         name='sub-deactivate'),
    # /manage/subscription/part
    path('manage/subscription/part/waitinglist', juntagrico_admin.part_waitinglist, name='sub-mgmt-part-waitinglist'),
    path('manage/subscription/part/canceledlist', juntagrico_admin.part_canceledlist,
         name='sub-mgmt-part-canceledlist'),
    path('manage/subscription/part/<int:part_id>/activate/', juntagrico_subscription.activate_part,
         name='part-activate'),
    path('manage/subscription/part/<int:part_id>/deactivate/', juntagrico_subscription.deactivate_part,
         name='part-deactivate'),
    path('manage/subscription/parts/apply', manage.parts_apply, name='parts-apply'),
    # /manage/subscription/extra
    path('my/extra/waitinglist', juntagrico_admin.extra_waitinglist, name='sub-mgmt-extra-waitinglist'),
    path('my/extra/canceledlist', juntagrico_admin.extra_canceledlist, name='sub-mgmt-extra-canceledlist'),
    # /manage/subscription/depot
    path('manage/subscription/depot/changes', manage.SubscriptionDepotChangesView.as_view(), name='manage-sub-depot-changes'),
    path('manage/subscription/depot/change/confirm', manage.subscription_depot_change_confirm, name='manage-sub-depot-change-confirm'),
    path('manage/subscription/depot/change/confirm/<int:subscription_id>', manage.subscription_depot_change_confirm, name='manage-sub-depot-change-confirm-single'),

    # /manage/member
    path('manage/member', manage.MemberView.as_view(), name='manage-member'),
    path('manage/member/active', manage.MemberActiveView.as_view(), name='manage-member-active'),
    path('manage/member/canceled', manage.MemberCanceledView.as_view(), name='manage-member-canceled'),
    path('manage/member/deactivate', manage.member_deactivate, name='manage-member-deactivate'),
    path('manage/member/deactivate/<int:member_id>/', manage.member_deactivate,
         name='manage-member-deactivate-single'),

    # /manage/assignments
    path('manage/assignments', manage.AssignmentsView.as_view(), name='manage-assignments'),
    # /manage/share
    path('manage/share/unpaid', manage.ShareUnpaidView.as_view(), name='manage-share-unpaid'),
    path('manage/share/canceled', manage.ShareCanceledView.as_view(), name='manage-share-canceled'),
    path('manage/share/payout', manage.share_payout, name='manage-share-payout'),
    path('manage/share/payout/<int:share_id>', manage.share_payout, name='manage-share-payout-single'),
    # /manage/depot
    path('manage/depot/<int:depot_id>/subscription', manage.DepotSubscriptionView.as_view(),
         name='manage-depot-subs'),
    # /manage/area
    path('manage/area/<int:area_id>/member', manage.AreaMemberView.as_view(), name='manage-area-member'),

    # /email
    path('my/mails', juntagrico_admin.mails, name='mail'),
    path('email/to/<int:member_id>', email.to_member, name='email-to-member'),
    path('my/mails/send', juntagrico_admin.send_email, name='mail-send'),
    path('my/mails/send/result/<int:numsent>/', juntagrico_admin.send_email_result, name='mail-result'),
    # /email/depot
    path('my/mails/depot', juntagrico_admin.mails_depot, name='mail-depot'),
    path('my/mails/send/depot', juntagrico_admin.send_email_depot, name='mail-depot-send'),
    # /email/area
    path('my/mails/area', juntagrico_admin.mails_area, name='mail-area'),
    path('my/mails/send/area', juntagrico_admin.send_email_area, name='mail-area-send'),
    # /email/job
    path('my/mails/job', juntagrico_admin.mails_job, name='mail-job'),
    path('my/mails/send/job', juntagrico_admin.send_email_job, name='mail-job-send'),
    # /email/template
    path('my/mailtemplate/<int:template_id>/', juntagrico_admin.get_mail_template, name='mail-template'),

    # /list
    path('my/pdf/depotlist', juntagrico_admin.depotlist, name='lists-depotlist'),
    path('my/pdf/depotoverview', juntagrico_admin.depot_overview, name='lists-depot-overview'),
    path('my/pdf/amountoverview', juntagrico_admin.amount_overview, name='lists-depot-amountoverview'),

    # /manage/list
    path('manage/list', juntagrico_admin.manage_list, name='manage-list'),

    # /export
    path('my/export', juntagrico_admin.export, name='export'),
    path('my/export/membersfilter', juntagrico_admin.excel_export_members_filter, name='export-membersfilter'),
    path('my/export/members', juntagrico_admin.excel_export_members, name='export-members'),
    path('my/export/shares', juntagrico_admin.excel_export_shares, name='export-shares'),
    path('my/export/subscriptions', juntagrico_admin.excel_export_subscriptions, name='export-subscriptions'),

    # /command
    path('command/shifttime', ShiftTimeFormView.as_view(), name='command-shifttime'),
    path('command/shifttime/success', ShiftTimeFormView.as_view(success=True), name='command-shifttime-success'),

    # /api
    # /api/share
    path('my/iso20022/shares/pain001', juntagrico_iso20022.share_pain001, name='share-pain001'),

    # /api/jobtype
    path('api/jobtype/<int:id>/description', api.job_type_description, name='api-jobtype-description'),
    path('api/jobtype/<int:id>/duration', api.job_type_duration, name='api-jobtype-duration'),

    # /js
    path('my/js/i18n', juntagrico.i18njs, name='js-i18n'),

    # /versions
    path('my/versions', juntagrico_admin.versions, name='versions')

]
