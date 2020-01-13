from django.conf.urls import include
from django.urls import path
from django.conf import settings
from django.contrib import admin

if settings.ADMIN_ENABLED:
    admin.autodiscover()

urlpatterns = [
    path('accounts/', include('users.urls')),
    path('', include('website.urls'))
]

if settings.ADMIN_ENABLED:
    urlpatterns.append(path('admin/', admin.site.urls)) 

if settings.PROFILE:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
