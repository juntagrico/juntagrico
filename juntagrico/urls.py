from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LoginView

from juntagrico import views as juntagrico
from juntagrico import views_admin as juntagrico_admin
from juntagrico import views_subscription as juntagrico_subscription
from juntagrico.personalisation import personal_urls

urlpatterns = [
    # general juntagrico stuff
    url('^my/home$', juntagrico.home),
    url('^my/password$', juntagrico.change_password),
    url('^my/jobs/(?P<job_id>.*?)/', juntagrico.job),
    url('^my/teams/(?P<area_id>.*?)/', juntagrico.team),
    url('^my/profile$', juntagrico.profile),
    url('^my/participation$', juntagrico.participation),
    url('^my/contact$', juntagrico.contact),
    url('^my/contact/member/(?P<member_id>.*?)/(?P<job_id>.*?)/', juntagrico.contact_member),
    url('^my/assignments$', juntagrico.assignments),
    url('^my/assignments/all$', juntagrico.assingments_all),
    url('^my/pastjobs$', juntagrico.pastjobs),
    url('^my/depot/(?P<depot_id>.*?)/', juntagrico.depot),
    url('^my/newpassword$', juntagrico.new_password),
    url('^my/sendconfirm$', juntagrico.send_confirm),
    url('^my/info/unpaidshares$', juntagrico.info_unpaid_shares),
    url(r'^logout/$', juntagrico.logout_view),
    url(r'^accounts/login/$', LoginView.as_view()),

    # subscription related juntagrico stuff
    url('^my/subscription$', juntagrico_subscription.subscription),
    url('^my/subscription/change$', juntagrico_subscription.subscription_change),
    url('^my/subscription/change/depot$', juntagrico_subscription.depot_change),
    url('^my/subscription/change/size$', juntagrico_subscription.size_change),
    url('^my/subscription/change/extra$', juntagrico_subscription.extra_change),
    url('^my/signup$', juntagrico_subscription.signup),
    url('^my/cosubmember/(?P<subscription_id>.*?)/', juntagrico_subscription.add_member),
    url('^my/create/subscrition$', juntagrico_subscription.createsubscription),
    url('^my/create/subscription/cancel$', juntagrico_subscription.cancel_create_subscription),
    url('^my/welcome$', juntagrico_subscription.welcome),
    url('^my/confirm/(?P<hash>.*?)/', juntagrico_subscription.confirm),
    url('^my/subscription/activate/(?P<subscription_id>.*?)/', juntagrico_subscription.activate_subscription),
    url('^my/subscription/deactivate/(?P<subscription_id>.*?)/', juntagrico_subscription.deactivate_subscription),
    url('^my/subscription/cancel/(?P<subscription_id>.*?)/', juntagrico_subscription.cancel_subscription),
    url('^my/type/change/(?P<subscription_id>.*?)/', juntagrico_subscription.activate_future_types),
    url('^my/extra/activate/(?P<extra_id>.*?)/', juntagrico_subscription.activate_extra),
    url('^my/extra/deactivate/(?P<extra_id>.*?)/', juntagrico_subscription.deactivate_extra),
    url('^my/extra/cancel/(?P<extra_id>.*?)/', juntagrico_subscription.cancel_extra),
    url('^my/order/share/$', juntagrico_subscription.order_shares),
    url('^my/order/share/success$', juntagrico_subscription.order_shares_success),

    # admin related juntagrico stuff
    url('^my/mails/send/depot$', juntagrico_admin.send_email_depot),
    url('^my/mails/send/area$', juntagrico_admin.send_email_area),
    url('^my/mails/send$', juntagrico_admin.send_email),
    url('^my/mails/send/result/(?P<numsent>.*?)/', juntagrico_admin.send_email_result),
    url('^my/mails$', juntagrico_admin.mails),
    url('^my/mails/depot$', juntagrico_admin.mails_depot),
    url('^my/mails/area$', juntagrico_admin.mails_area),
    url('^my/filters$', juntagrico_admin.filters),
    url('^my/filters/depot/(?P<depot_id>.*?)/', juntagrico_admin.filters_depot),
    url('^my/filters/area/(?P<area_id>.*?)/', juntagrico_admin.filters_area),
    url('^my/subscriptions$', juntagrico_admin.subscriptions),
    url('^my/subscriptions/depot/(?P<depot_id>.*?)/', juntagrico_admin.filter_subscriptions_depot),
    url('^my/future', juntagrico_admin.future),
    url('^my/export$', juntagrico_admin.export),
    url('^my/export/membersfilter$', juntagrico_admin.excel_export_members_filter),
    url('^my/export/members', juntagrico_admin.excel_export_members),
    url('^my/export/shares$', juntagrico_admin.excel_export_shares),
    url('^my/mailtemplate/(?P<template_id>.*?)/', juntagrico_admin.get_mail_template),
    url('^my/waitinglist', juntagrico_admin.waitinglist),
    url('^my/canceledlist', juntagrico_admin.canceledlist),
    url('^my/typechangedlist', juntagrico_admin.typechangelist),
    url('^my/extra/waitinglist', juntagrico_admin.extra_waitinglist),
    url('^my/extra/canceledlist', juntagrico_admin.extra_canceledlist),
    url('^my/maps', juntagrico_admin.maps),

    url(r'^my', include(personal_urls)),
]
