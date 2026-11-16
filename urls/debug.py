from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('admin/shell/', include('django_admin_shell.urls')),
    path('', include('urls.dev')),
] + debug_toolbar_urls()
