from django.conf.urls import include, url

from django.conf import settings
from django.views.generic import RedirectView
from juntagrico import views as juntagrico
from juntagrico import views_abo as juntagrico_abo
from juntagrico import views_admin as juntagrico_admin
from juntagrico.personalisation import personal_urls

import django



urls = [
    #general my ortoloco stuff
    url('^/home$', juntagrico.my_home),
    url('^/passwort$', juntagrico.my_change_password),    
    url('^/jobs/(?P<job_id>.*?)/', juntagrico.my_job),
    url('^/teams/(?P<bereich_id>.*?)/', juntagrico.my_team),
    url('^/profil$', juntagrico.my_profile),
    url('^/mitarbeit$', juntagrico.my_participation),
    url('^/kontakt$', juntagrico.my_contact),
    url('^/kontakt/loco/(?P<loco_id>.*?)/(?P<job_id>.*?)/', juntagrico.my_contact_loco),
    url('^/einsaetze$', juntagrico.my_einsaetze),
    url('^/einsaetze/alle$', juntagrico.my_einsaetze_all),
    url('^/vergangenejobs$', juntagrico.my_pastjobs),
    url('^/depot/(?P<depot_id>.*?)/', juntagrico.my_depot),
    url('^/neuespasswort$', juntagrico.my_new_password),
    url(r'^logout/$', juntagrico.logout_view),
    
    # abo related my ortoloco stuff
    url('^/abo$', juntagrico_abo.my_abo),
    url('^/abo/(?P<abo_id>.*?)/aendern$', juntagrico_abo.my_abo_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/depot$', juntagrico_abo.my_depot_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/groesse$', juntagrico_abo.my_size_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/extra$', juntagrico_abo.my_extra_change),
    url('^/anmelden$', juntagrico_abo.my_signup),
    url('^/abonnent/(?P<abo_id>.*?)/', juntagrico_abo.my_add_loco),
    url('^/aboerstellen$', juntagrico_abo.my_createabo),
    url('^/willkommen$', juntagrico_abo.my_welcome),
    url('^/bestaetigung/(?P<hash>.*?)/', juntagrico_abo.my_confirm),
    
    # admin related my ortoloco stuff
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
    url('^/abos$', juntagrico_admin.my_abos),
    url('^/abos/depot/(?P<depot_id>.*?)/', juntagrico_admin.my_abos_depot),
    #url('^my/depotlisten', juntagrico_admin.my_depotlisten),
    url('^exports/depotlisten/(?P<name>.*)', juntagrico_admin.alldepots_list),
    url('^/zukunft', juntagrico_admin.my_future),
    url('^/wechsel/zusatzabos', juntagrico_admin.my_switch_extras),
    url('^/wechsel/abos', juntagrico_admin.my_switch_abos),    
    url('^/export$', juntagrico_admin.my_export),
    url('^/export/locosfilter$', juntagrico_admin.my_excel_export_locos_filter),
    url('^/export/locos', juntagrico_admin.my_excel_export_locos),
    url('^/export/shares$', juntagrico_admin.my_excel_export_shares),
    url('^/mailtemplate/(?P<template_id>.*?)/', juntagrico_admin.my_get_mail_template),
    url('^/waitinglist', my_ortoloco_admin.waitinglist),
    url('^/maps', juntagrico_admin.my_maps),
    
    url(r'^', include(personal_urls)),
]
