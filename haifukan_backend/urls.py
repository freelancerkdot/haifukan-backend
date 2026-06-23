"""
URL configuration for haifukan_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/admin/", include("admin.urls")),
    path("api/misc/", include("misc.urls")),
    path("api/core/", include("core.urls")),
]

# Serve uploaded media files through Django. This works in development and
# also on hosts like PythonAnywhere (even with DEBUG=False) where you may not
# want to configure a separate static mapping. For high-traffic production,
# prefer the host's static-file mapping (/media/ -> MEDIA_ROOT) instead.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
