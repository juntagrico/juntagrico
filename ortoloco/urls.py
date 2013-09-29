from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()
from django.contrib.auth.views import login, logout
from django.views.generic import RedirectView



urlpatterns = patterns('',
	url('^$', 'my_ortoloco.views.home'),
	url('^aktuelles', 'my_ortoloco.views.home'),
	url('^idee', 'my_ortoloco.views.about'),
	url('^portrait', 'my_ortoloco.views.portrait'),
	url('^hintergrund', 'my_ortoloco.views.background'),
	url('^abo', 'my_ortoloco.views.abo'),
	url('^faq', 'my_ortoloco.views.faq'),
	url('^mitmachen', 'my_ortoloco.views.join'),
	url('^galerie', RedirectView.as_view(url='/photologue/gallery/page/1/')),
	url('^medien', 'my_ortoloco.views.media'),
    url('^kontakt', 'my_ortoloco.views.contact'),

    #url('^myortoloco/', 'my_ortoloco.views.myortoloco_home'),
    url('^myortoloco/home.html', 'my_ortoloco.views.myortoloco_home'),
    url('^myortoloco/jobs/(?P<job_id>.*?)/', 'my_ortoloco.views.myortoloco_job'),
    url('^myortoloco/teams/(?P<bereich_id>.*?)/', 'my_ortoloco.views.myortoloco_team'),
    url('^myortoloco/personal_info', 'my_ortoloco.views.myortoloco_personal_info'),


    (r'^accounts/login/$',  login),
    (r'^logout/$', 'my_ortoloco.views.logout_view'),

    (r'^photologue/', include('photologue.urls')),

    url('^depots/', 'my_ortoloco.views.all_depots'),
    url('^depotliste/(?P<name_or_id>.*?)/', 'my_ortoloco.views.depot_list'),

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
