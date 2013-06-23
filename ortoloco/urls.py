from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
	url('^$', 'loco_app.views.home'),
	url('^web/home.html', 'loco_app.views.home'),
	url('^web/about.html', 'loco_app.views.about'),
	url('^web/portrait.html', 'loco_app.views.portrait'),
	url('^web/background.html', 'loco_app.views.background'),
	url('^web/abo.html', 'loco_app.views.abo'),
	url('^web/join.html', 'loco_app.views.join'),
	url('^web/gallery.html', 'loco_app.views.gallery'),
	url('^web/media.html', 'loco_app.views.media'),
    url('^web/downloads.html', 'loco_app.views.downloads'),
    url('^web/links.html', 'loco_app.views.links'),
    url('^web/contact.html', 'loco_app.views.contact'),

    url('^depots/', 'loco_app.views.all_depots'),
    url('^depotliste/(?P<name_or_id>.*?)/', 'loco_app.views.depot_list'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^tinymce/', include('tinymce.urls')),
    url(r'^medias/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),

)
