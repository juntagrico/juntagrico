from django.urls import path, include


urlpatterns = [
    path('', include('urls.minimal')),
    path('', include('juntagrico_legacy.urls')),
    path('', include('juntagrico_legacy.downgrade.urls_1_5')),
]
