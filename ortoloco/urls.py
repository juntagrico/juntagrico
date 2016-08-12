from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView
from static_ortoloco import views as static_ortoloco
from my_ortoloco import views as my_ortoloco
from my_ortoloco import views_abo as my_ortoloco_abo
from my_ortoloco import views_admin as my_ortoloco_admin

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
    
    #general my ortoloco stuff
    url('^my/home$', my_ortoloco.my_home),
    url('^my/passwort$', my_ortoloco.my_change_password),    
    url('^my/jobs/(?P<job_id>.*?)/', my_ortoloco.my_job),
    url('^my/teams/(?P<bereich_id>.*?)/', my_ortoloco.my_team),
    url('^my/profil$', my_ortoloco.my_profile),
    url('^my/mitarbeit$', my_ortoloco.my_participation),
    url('^my/kontakt$', my_ortoloco.my_contact),
    url('^my/kontakt/loco/(?P<loco_id>.*?)/(?P<job_id>.*?)/', my_ortoloco.my_contact_loco),
    url('^my/einsaetze$', my_ortoloco.my_einsaetze),
    url('^my/einsaetze/alle$', my_ortoloco.my_einsaetze_all),
    url('^my/vergangenejobs$', my_ortoloco.my_pastjobs),
    url('^my/depot/(?P<depot_id>.*?)/', my_ortoloco.my_depot),
    url('^my/neuespasswort$', my_ortoloco.my_new_password),
    url(r'^logout/$', my_ortoloco.logout_view),
    
    # abo related my ortoloco stuff
    url('^my/abo$', my_ortoloco_abo.my_abo),
    url('^my/abo/(?P<abo_id>.*?)/aendern$', my_ortoloco_abo.my_abo_change),
    #url('^my/abo/(?P<abo_id>.*?)/aendern/depot$', my_ortoloco_abo.my_depot_change),
    url('^my/abo/(?P<abo_id>.*?)/aendern/groesse$', my_ortoloco_abo.my_size_change),
    url('^my/abo/(?P<abo_id>.*?)/aendern/extra$', my_ortoloco_abo.my_extra_change),
    url('^my/anmelden$', my_ortoloco_abo.my_signup),
    url('^my/abonnent/(?P<abo_id>.*?)/', my_ortoloco_abo.my_add_loco),
    url('^my/aboerstellen$', my_ortoloco_abo.my_createabo),
    url('^my/willkommen$', my_ortoloco_abo.my_welcome),
    url('^my/bestaetigung/(?P<hash>.*?)/', my_ortoloco_abo.my_confirm),
    
    # admin related my ortoloco stuff
    url('^my/politoloco$', my_ortoloco_admin.send_politoloco),
    url('^my/mails/send/depot$', my_ortoloco_admin.send_email_depot),
    url('^my/mails/send/area$', my_ortoloco_admin.send_email_area),
    url('^my/mails/send$', my_ortoloco_admin.send_email),
    url('^my/mails/send/result/(?P<numsent>.*?)/', my_ortoloco_admin.send_email_result),
    url('^my/mails$', my_ortoloco_admin.my_mails),
    url('^my/mails/depot$', my_ortoloco_admin.my_mails_depot),
    url('^my/mails/area$', my_ortoloco_admin.my_mails_area),
    url('^my/filters$', my_ortoloco_admin.my_filters),
    url('^my/filters/depot/(?P<depot_id>.*?)/', my_ortoloco_admin.my_filters_depot),
    url('^my/filters/area/(?P<area_id>.*?)/', my_ortoloco_admin.my_filters_area),
    url('^my/abos$', my_ortoloco_admin.my_abos),
    url('^my/abos/depot/(?P<depot_id>.*?)/', my_ortoloco_admin.my_abos_depot),
    url('^my/depotlisten', my_ortoloco_admin.my_depotlisten),
    url('^exports/depotlisten/(?P<name>.*)', my_ortoloco_admin.alldepots_list),
    url('^my/zukunft', my_ortoloco_admin.my_future),
    url('^my/wechsel/zusatzabos', my_ortoloco_admin.my_switch_extras),
    url('^my/wechsel/abos', my_ortoloco_admin.my_switch_abos),    
    url('^my/export$', my_ortoloco_admin.my_export),
    url('^my/export/locosfilter$', my_ortoloco_admin.my_excel_export_locos_filter),
    url('^my/export/locos', my_ortoloco_admin.my_excel_export_locos),
    url('^my/export/shares$', my_ortoloco_admin.my_excel_export_shares),
    
    url(r'^impersonate/', include('impersonate.urls')),

    url(r'^accounts/login/$',  login),

    url(r'^photologue/', include('photologue.urls')),

    
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
