from django.conf.urls import include, url
from my_ortoloco.personalisation import personal_views as my_ortoloco_personal

urlpatterns = [
    url('^my/politoloco$', my_ortoloco_personal.send_politoloco),
    url(r'^photologue/', include('photologue.urls')),
]
