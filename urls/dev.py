from django.urls import path, include


urlpatterns = [
    path('djrichtextfield/', include('djrichtextfield.urls')),
    path('', include('urls.minimal')),
]
