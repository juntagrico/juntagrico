from django.conf.urls import patterns, include, url

from static_ortoloco import views as static_ortoloco

urlpatterns = [
	url('^$', static_ortoloco.myredirect),
	
]
