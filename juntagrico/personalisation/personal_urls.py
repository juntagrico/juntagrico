from django.conf.urls import include, url
from juntagrico.personalisation import personal_views as juntagrico_personal

urlpatterns = [
    url('^politoloco$', juntagrico_personal.send_politoloco),
    url(r'^photologue/', include('photologue.urls')),
]
