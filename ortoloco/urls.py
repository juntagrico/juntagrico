from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView

import django_cron
django_cron.autodiscover()



urlpatterns = patterns('',
	url('^$', 'static_ortoloco.views.home'),
	url('^aktuelles$', 'static_ortoloco.views.home'),
	url('^idee$', 'static_ortoloco.views.about'),
	url('^portrait$', 'static_ortoloco.views.portrait'),
	url('^hintergrund$', 'static_ortoloco.views.background'),
	url('^abo$', 'static_ortoloco.views.abo'),
	url('^faq$', 'static_ortoloco.views.faq'),
	url('^mitmachen$', 'static_ortoloco.views.join'),
	url('^galerie$', RedirectView.as_view(url='/photologue/gallery/page/1/')),
    url('^medien$', 'static_ortoloco.views.media'),
    url('^links$', 'static_ortoloco.views.links'),
    url('^dokumente$', 'static_ortoloco.views.documents'),
    url('^kontakt$', 'static_ortoloco.views.contact'),

    #url('^myortoloco/', 'my_ortoloco.views.myortoloco_home'),
    url('^my/home$', 'my_ortoloco.views.my_home'),
    url('^my/passwort$', 'my_ortoloco.views.my_change_password'),
    url('^my/abo$', 'my_ortoloco.views.my_abo'),
    url('^my/abo/(?P<abo_id>.*?)/aendern$', 'my_ortoloco.views.my_abo_change'),
    url('^my/abo/(?P<abo_id>.*?)/aendern/depot$', 'my_ortoloco.views.my_depot_change'),
    url('^my/abo/(?P<abo_id>.*?)/aendern/extra$', 'my_ortoloco.views.my_extra_change'),
    url('^my/abo/(?P<abo_id>.*?)/aendern/groesse$', 'my_ortoloco.views.my_size_change'),
    url('^my/jobs/(?P<job_id>.*?)/', 'my_ortoloco.views.my_job'),
    url('^my/teams/(?P<bereich_id>.*?)/', 'my_ortoloco.views.my_team'),
    url('^my/profil$', 'my_ortoloco.views.my_profile'),
    url('^my/mitarbeit$', 'my_ortoloco.views.my_participation'),
    url('^my/kontakt$', 'my_ortoloco.views.my_contact'),
    url('^my/einsaetze$', 'my_ortoloco.views.my_einsaetze'),
    url('^my/einsaetze/alle$', 'my_ortoloco.views.my_einsaetze_all'),
    url('^my/anmelden$', 'my_ortoloco.views.my_signup'),
    url('^my/aboerstellen$', 'my_ortoloco.views.my_createabo'),
    url('^my/willkommen$', 'my_ortoloco.views.my_welcome'),
    url('^my/vergangenejobs$', 'my_ortoloco.views.my_pastjobs'),
    url('^my/abonnent/(?P<abo_id>.*?)/', 'my_ortoloco.views.my_add_loco'),
    url('^my/depot/(?P<depot_id>.*?)/', 'my_ortoloco.views.my_depot'),
    url('^my/mails$', 'my_ortoloco.views.my_mails'),
    url('^my/mails_depot$', 'my_ortoloco.views.my_mails_depot'),
    url('^my/mails/send$', 'my_ortoloco.views.send_email'),
    url('^my/mails/send_to_depot$', 'my_ortoloco.views.send_email_to_depot'),
    url('^my/depotlisten', 'my_ortoloco.views.my_depotlisten'),
    url('^my/neuespasswort$', 'my_ortoloco.views.my_new_password'),
    url('^my/bestaetigung/(?P<hash>.*?)/', 'my_ortoloco.views.my_confirm'),
    url('^my/politoloco$', 'my_ortoloco.views.send_politoloco'),
    url('^my/filters$', 'my_ortoloco.views.my_filters'),
    url('^my/filters_depot', 'my_ortoloco.views.my_filters_depot'),
    url('^my/abos$', 'my_ortoloco.views.my_abos'),
    url('^my/abos_depot', 'my_ortoloco.views.my_abos_depot'),
    url('^my/zukunft', 'my_ortoloco.views.my_future'),
    url('^my/wechsel/zusatzabos', 'my_ortoloco.views.my_switch_extras'),
    url('^my/wechsel/abos', 'my_ortoloco.views.my_switch_abos'),

    url(r'^impersonate/', include('impersonate.urls')),

    #url('^my/createlocoforsuperuserifnotexist$', 'my_ortoloco.views.my_createlocoforsuperuserifnotexist'),
    #url('^my/startmigrationonceassuperadmin$', 'my_ortoloco.views.my_startmigration'),
    url('^my/migratedbtonewestversion', 'my_ortoloco.views.migrate_apps'),
    url('^pipinstallrrequirements', 'my_ortoloco.views.pip_install'),
    url('^mini_migrate_future_zusatzabos', 'my_ortoloco.views.mini_migrate_future_zusatzabos'),


    (r'^accounts/login/$',  login),
    (r'^logout/$', 'my_ortoloco.views.logout_view'),

    (r'^photologue/', include('photologue.urls')),

    url('^exports/depotlisten/(?P<name>.*)', 'my_ortoloco.views.alldepots_list'),
    #url('^test_filters/$', 'my_ortoloco.views.test_filters'),
    #url('^test_filters_post/$', 'my_ortoloco.views.test_filters_post'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #(r'^tinymce/', include('tinymce.urls')),
    url(r'^medias/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
	url(r'^downloads/(?P<param>.*)$', RedirectView.as_view(url='/medias/downloads/%(param)s')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),

)
