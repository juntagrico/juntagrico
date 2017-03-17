from django.conf.urls import include, url

from django.conf import settings
from django.views.generic import RedirectView
from django.contrib.auth.views import login, logout
from juntagrico import views as juntagrico
from juntagrico import views_subscription as juntagrico_subscription
from juntagrico import views_admin as juntagrico_admin
from juntagrico.personalisation import personal_urls
from django.contrib import admin

import django



urlpatterns = [
    #general juntagrico stuff
    url('^my/home$', juntagrico.my_home),
    url('^my/passwort$', juntagrico.my_change_password),    
    url('^my/jobs/(?P<job_id>.*?)/', juntagrico.my_job),
    url('^my/teams/(?P<area_id>.*?)/', juntagrico.my_team),
    url('^my/profil$', juntagrico.my_profile),
    url('^my/mitarbeit$', juntagrico.my_participation),
    url('^my/kontakt$', juntagrico.my_contact),
    url('^my/kontakt/member/(?P<member_id>.*?)/(?P<job_id>.*?)/', juntagrico.my_contact_member),
    url('^my/einsaetze$', juntagrico.my_assignments),
    url('^my/einsaetze/alle$', juntagrico.my_assingments_all),
    url('^my/vergangenejobs$', juntagrico.my_pastjobs),
    url('^my/depot/(?P<depot_id>.*?)/', juntagrico.my_depot),
    url('^my/neuespasswort$', juntagrico.my_new_password),
    url(r'^logout/$', juntagrico.logout_view),
    url(r'^accounts/login/$',  login),
    
    # subscription related juntagrico stuff
    url('^my/subscription$', juntagrico_subscription.my_subscription),
    url('^my/subscription/(?P<subscription_id>.*?)/aendern$', juntagrico_subscription.my_subscription_change),
    url('^my/subscription/(?P<subscription_id>.*?)/aendern/depot$', juntagrico_subscription.my_depot_change),
    url('^my/subscription/(?P<subscription_id>.*?)/aendern/groesse$', juntagrico_subscription.my_size_change),
    url('^my/subscription/(?P<subscription_id>.*?)/aendern/extra$', juntagrico_subscription.my_extra_change),
    url('^my/anmelden$', juntagrico_subscription.my_signup),
    url('^my/subscriptionnnent/(?P<subscription_id>.*?)/', juntagrico_subscription.add_member),
    url('^my/subscriptionerstellen$', juntagrico_subscription.createsubscription),
    url('^my/willkommen$', juntagrico_subscription.my_welcome),
    url('^my/bestaetigung/(?P<hash>.*?)/', juntagrico_subscription.my_confirm),
    
    # admin related juntagrico stuff
    url('^my/mails/send/depot$', juntagrico_admin.send_email_depot),
    url('^my/mails/send/area$', juntagrico_admin.send_email_area),
    url('^my/mails/send$', juntagrico_admin.send_email),
    url('^my/mails/send/result/(?P<numsent>.*?)/', juntagrico_admin.send_email_result),
    url('^my/mails$', juntagrico_admin.my_mails),
    url('^my/mails/depot$', juntagrico_admin.my_mails_depot),
    url('^my/mails/area$', juntagrico_admin.my_mails_area),
    url('^my/filters$', juntagrico_admin.my_filters),
    url('^my/filters/depot/(?P<depot_id>.*?)/', juntagrico_admin.my_filters_depot),
    url('^my/filters/area/(?P<area_id>.*?)/', juntagrico_admin.my_filters_area),
    url('^my/subscriptions$', juntagrico_admin.my_subscriptions),
    url('^my/subscriptions/depot/(?P<depot_id>.*?)/', juntagrico_admin.my_subscriptions_depot),
    #url('^my/depotlisten', juntagrico_admin.my_depotlists),
    url('^my/exports/depotlisten/(?P<name>.*)', juntagrico_admin.alldepots_list),
    url('^my/zukunft', juntagrico_admin.my_future),
    url('^my/wechsel/zusatzsubscriptions', juntagrico_admin.my_switch_extras),
    url('^my/wechsel/subscriptions', juntagrico_admin.my_switch_subscriptions),    
    url('^my/export$', juntagrico_admin.my_export),
    url('^my/export/membersfilter$', juntagrico_admin.my_excel_export_members_filter),
    url('^my/export/members', juntagrico_admin.my_excel_export_members),
    url('^my/export/shares$', juntagrico_admin.my_excel_export_shares),
    url('^my/mailtemplate/(?P<template_id>.*?)/', juntagrico_admin.my_get_mail_template),
    url('^my/waitinglist', juntagrico_admin.waitinglist),
    url('^my/maps', juntagrico_admin.my_maps),

    
    url(r'^my', include(personal_urls)),
    url(r'^admin/', include(admin.site.urls)),
]
