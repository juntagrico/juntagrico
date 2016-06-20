from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView
from static_ortoloco import views as static_ortoloco
from my_ortoloco import views as my_ortoloco

import django
#import django_cron
#django_cron.autodiscover()



urlpatterns = [
	url('^$', static_ortoloco.home),
	url('^aktuelles$', static_ortoloco.home),
	url('^idee$', static_ortoloco.about),
	url('^portrait$', static_ortoloco.portrait),
	url('^hintergrund$', static_ortoloco.background),
	url('^abo$', static_ortoloco.abo),
	url('^faq$', static_ortoloco.faq),
	url('^mitmachen$', static_ortoloco.join),
	url('^galerie$', RedirectView.as_view(url='/photologue/gallery/page/1/')),
    url('^medien$', static_ortoloco.media),
    url('^links$', static_ortoloco.links),
    url('^dokumente$', static_ortoloco.documents),
    url('^kontakt$', static_ortoloco.contact),

    #url('^myortoloco/', my_ortoloco.myortoloco_home),
    url('^my/home$', my_ortoloco.my_home),
    url('^my/passwort$', my_ortoloco.my_change_password),
    url('^my/abo$', my_ortoloco.my_abo),
    url('^my/abo/(?P<abo_id>.*?)/aendern$', my_ortoloco.my_abo_change),
    #url('^my/abo/(?P<abo_id>.*?)/aendern/depot$', my_ortoloco.my_depot_change),
    url('^my/abo/(?P<abo_id>.*?)/aendern/extra$', my_ortoloco.my_extra_change),
    url('^my/abo/(?P<abo_id>.*?)/aendern/groesse$', my_ortoloco.my_size_change),
    url('^my/jobs/(?P<job_id>.*?)/', my_ortoloco.my_job),
    url('^my/teams/(?P<bereich_id>.*?)/', my_ortoloco.my_team),
    url('^my/profil$', my_ortoloco.my_profile),
    url('^my/mitarbeit$', my_ortoloco.my_participation),
    url('^my/kontakt$', my_ortoloco.my_contact),
    url('^my/kontakt/loco/(?P<loco_id>.*?)/(?P<job_id>.*?)/', my_ortoloco.my_contact_loco),
    url('^my/einsaetze$', my_ortoloco.my_einsaetze),
    url('^my/einsaetze/alle$', my_ortoloco.my_einsaetze_all),
    url('^my/anmelden$', my_ortoloco.my_signup),
    url('^my/aboerstellen$', my_ortoloco.my_createabo),
    url('^my/willkommen$', my_ortoloco.my_welcome),
    url('^my/vergangenejobs$', my_ortoloco.my_pastjobs),
    url('^my/abonnent/(?P<abo_id>.*?)/', my_ortoloco.my_add_loco),
    url('^my/depot/(?P<depot_id>.*?)/', my_ortoloco.my_depot),
    url('^my/mails$', my_ortoloco.my_mails),
    url('^my/mails/depot$', my_ortoloco.my_mails_depot),
    url('^my/mails/area$', my_ortoloco.my_mails_area),
    url('^my/mails/send$', my_ortoloco.send_email),
    url('^my/mails/send/result/(?P<numsent>.*?)/', my_ortoloco.send_email_result),
    url('^my/mails/send/depot$', my_ortoloco.send_email_depot),
    url('^my/mails/send/area$', my_ortoloco.send_email_area),
    url('^my/depotlisten', my_ortoloco.my_depotlisten),
    url('^my/export$', my_ortoloco.my_export),
    url('^my/export/locosfilter$', my_ortoloco.my_excel_export_locos_filter),
    url('^my/export/locos', my_ortoloco.my_excel_export_locos),
    url('^my/export/shares$', my_ortoloco.my_excel_export_shares),
    url('^my/neuespasswort$', my_ortoloco.my_new_password),
    url('^my/bestaetigung/(?P<hash>.*?)/', my_ortoloco.my_confirm),
    url('^my/politoloco$', my_ortoloco.send_politoloco),
    url('^my/filters$', my_ortoloco.my_filters),
    url('^my/filters/depot/(?P<depot_id>.*?)/', my_ortoloco.my_filters_depot),
    url('^my/filters/area/(?P<area_id>.*?)/', my_ortoloco.my_filters_area),
    url('^my/abos$', my_ortoloco.my_abos),
    url('^my/abos/depot/(?P<depot_id>.*?)/', my_ortoloco.my_abos_depot),
    url('^my/zukunft', my_ortoloco.my_future),
    url('^my/wechsel/zusatzabos', my_ortoloco.my_switch_extras),
    url('^my/wechsel/abos', my_ortoloco.my_switch_abos),

    url(r'^impersonate/', include('impersonate.urls')),

    url('^my/createlocoforsuperuserifnotexist$', my_ortoloco.my_createlocoforsuperuserifnotexist),
    #url('^my/startmigrationonceassuperadmin$', my_ortoloco.my_startmigration),
    url('^my/migratedbtonewestversion', my_ortoloco.migrate_apps),
    url('^pipinstallrrequirements', my_ortoloco.pip_install),


    url(r'^accounts/login/$',  login),
    url(r'^logout/$', my_ortoloco.logout_view),

    url(r'^photologue/', include('photologue.urls')),

    url('^exports/depotlisten/(?P<name>.*)', my_ortoloco.alldepots_list),
    #url('^test_filters/$', my_ortoloco.test_filters),
    #url('^test_filters_post/$', my_ortoloco.test_filters_post),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls)),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #(r'^tinymce/', include('tinymce.urls')),
    #url(r'^medias/(?P<path>.*)$', django.views.static.serve, {
    #    'document_root': settings.MEDIA_ROOT,
    #}),
	#url(r'^downloads/(?P<param>.*)$', RedirectView.as_view(url='/medias/downloads/%(param)s')),
    #url(r'^static/(?P<path>.*)$', django.views.static.serve, {
    #   'document_root': settings.STATIC_ROOT,
    #})
]
