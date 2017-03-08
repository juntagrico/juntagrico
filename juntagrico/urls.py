from django.conf.urls import include, url

from django.conf import settings
from django.views.generic import RedirectView
from juntagrico import views as juntagrico
from juntagrico import views_subscription as juntagrico_subscription
from juntagrico import views_admin as juntagrico_admin
from juntagrico.personalisation import personal_urls

import django



urls = [
    #general juntagrico stuff
    url('^/home$', juntagrico.my_home),
    url('^/passwort$', juntagrico.my_change_password),    
    url('^/jobs/(?P<job_id>.*?)/', juntagrico.my_job),
    url('^/teams/(?P<bereich_id>.*?)/', juntagrico.my_team),
    url('^/profil$', juntagrico.my_profile),
    url('^/mitarbeit$', juntagrico.my_participation),
    url('^/kontakt$', juntagrico.my_contact),
    url('^/kontakt/member/(?P<member_id>.*?)/(?P<job_id>.*?)/', juntagrico.my_contact_member),
    url('^/einsaetze$', juntagrico.my_assignments),
    url('^/einsaetze/alle$', juntagrico.my_assingments_all),
    url('^/vergangenejobs$', juntagrico.my_pastjobs),
    url('^/depot/(?P<depot_id>.*?)/', juntagrico.my_depot),
    url('^/neuespasswort$', juntagrico.my_new_password),
    url(r'^logout/$', juntagrico.logout_view),
    
    # subscription related juntagrico stuff
    url('^/subscription$', juntagrico_subscription.my_subscription),
    url('^/subscription/(?P<subscription_id>.*?)/aendern$', juntagrico_subscription.my_subscription_change),
    url('^/subscription/(?P<subscription_id>.*?)/aendern/depot$', juntagrico_subscription.my_depot_change),
    url('^/subscription/(?P<subscription_id>.*?)/aendern/groesse$', juntagrico_subscription.my_size_change),
    url('^/subscription/(?P<subscription_id>.*?)/aendern/extra$', juntagrico_subscription.my_extra_change),
    url('^/anmelden$', juntagrico_subscription.my_signup),
    url('^/subscriptionnnent/(?P<subscription_id>.*?)/', juntagrico_subscription.my_add_member),
    url('^/subscriptionerstellen$', juntagrico_subscription.my_createsubscription),
    url('^/willkommen$', juntagrico_subscription.my_welcome),
    url('^/bestaetigung/(?P<hash>.*?)/', juntagrico_subscription.my_confirm),
    
    # admin related juntagrico stuff
    url('^/mails/send/depot$', juntagrico_admin.send_email_depot),
    url('^/mails/send/area$', juntagrico_admin.send_email_area),
    url('^/mails/send$', juntagrico_admin.send_email),
    url('^/mails/send/result/(?P<numsent>.*?)/', juntagrico_admin.send_email_result),
    url('^/mails$', juntagrico_admin.my_mails),
    url('^/mails/depot$', juntagrico_admin.my_mails_depot),
    url('^/mails/area$', juntagrico_admin.my_mails_area),
    url('^/filters$', juntagrico_admin.my_filters),
    url('^/filters/depot/(?P<depot_id>.*?)/', juntagrico_admin.my_filters_depot),
    url('^/filters/area/(?P<area_id>.*?)/', juntagrico_admin.my_filters_area),
    url('^/subscriptions$', juntagrico_admin.my_subscriptions),
    url('^/subscriptions/depot/(?P<depot_id>.*?)/', juntagrico_admin.my_subscriptions_depot),
    #url('^my/depotlisten', juntagrico_admin.my_depotlists),
    url('^exports/depotlisten/(?P<name>.*)', juntagrico_admin.alldepots_list),
    url('^/zukunft', juntagrico_admin.my_future),
    url('^/wechsel/zusatzsubscriptions', juntagrico_admin.my_switch_extras),
    url('^/wechsel/subscriptions', juntagrico_admin.my_switch_subscriptions),    
    url('^/export$', juntagrico_admin.my_export),
    url('^/export/membersfilter$', juntagrico_admin.my_excel_export_members_filter),
    url('^/export/members', juntagrico_admin.my_excel_export_members),
    url('^/export/shares$', juntagrico_admin.my_excel_export_shares),
    url('^/mailtemplate/(?P<template_id>.*?)/', juntagrico_admin.my_get_mail_template),
    url('^/waitinglist', juntagrico_admin.waitinglist),
    url('^/maps', juntagrico_admin.my_maps),
    
    url(r'^', include(personal_urls)),
]
