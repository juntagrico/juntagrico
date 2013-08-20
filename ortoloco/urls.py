from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView



urlpatterns = patterns('',
	url('^$', 'loco_app.views.home'),
	url('^aktuelles', 'loco_app.views.home'),
	url('^idee', 'loco_app.views.about'),
	url('^portrait', 'loco_app.views.portrait'),
	url('^hintergrund', 'loco_app.views.background'),
	url('^abo', 'loco_app.views.abo'),
	url('^faq', 'loco_app.views.faq'),
	url('^mitmachen', 'loco_app.views.join'),
	url('^galerie', RedirectView.as_view(url='/photologue/gallery/page/1/')),
	url('^medien', 'loco_app.views.media'),
    url('^kontakt', 'loco_app.views.contact'),

    url('^myortoloco/home.html', 'loco_app.views.myortoloco_home'),
    url('^myortoloco/jobs/(?P<job_id>.*?)/', 'loco_app.views.myortoloco_job'),
    url('^myortoloco/teams/(?P<bereich_id>.*?)/', 'loco_app.views.myortoloco_team'),
    url('^myortoloco/personal_info', 'loco_app.views.myortoloco_personal_info'),


    (r'^accounts/login/$',  login),
    (r'^logout/$', 'loco_app.views.logout'),

    (r'^photologue/', include('photologue.urls')),

    url('^depots/', 'loco_app.views.all_depots'),
    url('^depotliste/(?P<name_or_id>.*?)/', 'loco_app.views.depot_list'),

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
