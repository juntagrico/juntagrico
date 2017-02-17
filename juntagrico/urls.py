from django.conf.urls import include, url

from django.conf import settings
from django.views.generic import RedirectView
from my_ortoloco import views as my_ortoloco
from my_ortoloco import views_abo as my_ortoloco_abo
from my_ortoloco import views_admin as my_ortoloco_admin
from my_ortoloco.personalisation import personal_urls

import django



urls = [
    #general my ortoloco stuff
    url('^/home$', my_ortoloco.my_home),
    url('^/passwort$', my_ortoloco.my_change_password),    
    url('^/jobs/(?P<job_id>.*?)/', my_ortoloco.my_job),
    url('^/teams/(?P<bereich_id>.*?)/', my_ortoloco.my_team),
    url('^/profil$', my_ortoloco.my_profile),
    url('^/mitarbeit$', my_ortoloco.my_participation),
    url('^/kontakt$', my_ortoloco.my_contact),
    url('^/kontakt/loco/(?P<loco_id>.*?)/(?P<job_id>.*?)/', my_ortoloco.my_contact_loco),
    url('^/einsaetze$', my_ortoloco.my_einsaetze),
    url('^/einsaetze/alle$', my_ortoloco.my_einsaetze_all),
    url('^/vergangenejobs$', my_ortoloco.my_pastjobs),
    url('^/depot/(?P<depot_id>.*?)/', my_ortoloco.my_depot),
    url('^/neuespasswort$', my_ortoloco.my_new_password),
    url(r'^logout/$', my_ortoloco.logout_view),
    
    # abo related my ortoloco stuff
    url('^/abo$', my_ortoloco_abo.my_abo),
    url('^/abo/(?P<abo_id>.*?)/aendern$', my_ortoloco_abo.my_abo_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/depot$', my_ortoloco_abo.my_depot_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/groesse$', my_ortoloco_abo.my_size_change),
    url('^/abo/(?P<abo_id>.*?)/aendern/extra$', my_ortoloco_abo.my_extra_change),
    url('^/anmelden$', my_ortoloco_abo.my_signup),
    url('^/abonnent/(?P<abo_id>.*?)/', my_ortoloco_abo.my_add_loco),
    url('^/aboerstellen$', my_ortoloco_abo.my_createabo),
    url('^/willkommen$', my_ortoloco_abo.my_welcome),
    url('^/bestaetigung/(?P<hash>.*?)/', my_ortoloco_abo.my_confirm),
    
    # admin related my ortoloco stuff
    url('^/mails/send/depot$', my_ortoloco_admin.send_email_depot),
    url('^/mails/send/area$', my_ortoloco_admin.send_email_area),
    url('^/mails/send$', my_ortoloco_admin.send_email),
    url('^/mails/send/result/(?P<numsent>.*?)/', my_ortoloco_admin.send_email_result),
    url('^/mails$', my_ortoloco_admin.my_mails),
    url('^/mails/depot$', my_ortoloco_admin.my_mails_depot),
    url('^/mails/area$', my_ortoloco_admin.my_mails_area),
    url('^/filters$', my_ortoloco_admin.my_filters),
    url('^/filters/depot/(?P<depot_id>.*?)/', my_ortoloco_admin.my_filters_depot),
    url('^/filters/area/(?P<area_id>.*?)/', my_ortoloco_admin.my_filters_area),
    url('^/abos$', my_ortoloco_admin.my_abos),
    url('^/abos/depot/(?P<depot_id>.*?)/', my_ortoloco_admin.my_abos_depot),
    #url('^my/depotlisten', my_ortoloco_admin.my_depotlisten),
    url('^exports/depotlisten/(?P<name>.*)', my_ortoloco_admin.alldepots_list),
    url('^/zukunft', my_ortoloco_admin.my_future),
    url('^/wechsel/zusatzabos', my_ortoloco_admin.my_switch_extras),
    url('^/wechsel/abos', my_ortoloco_admin.my_switch_abos),    
    url('^/export$', my_ortoloco_admin.my_export),
    url('^/export/locosfilter$', my_ortoloco_admin.my_excel_export_locos_filter),
    url('^/export/locos', my_ortoloco_admin.my_excel_export_locos),
    url('^/export/shares$', my_ortoloco_admin.my_excel_export_shares),
    url('^/mailtemplate/(?P<template_id>.*?)/', my_ortoloco_admin.my_get_mail_template),
    url('^/maps', my_ortoloco_admin.my_maps),
    
    url(r'^', include(personal_urls)),
]
