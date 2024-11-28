"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from myapp.admin import PointAdmin, VisitAdmin, RoundAdmin, GuardAdmin, MyAdminSite
from myapp.models import Guard, Round, Visit, Point

static_urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}),
]

# admin_site = MyAdminSite()
#
# admin_site.register(Guard, GuardAdmin)
# admin_site.register(Round, RoundAdmin)
# admin_site.register(Visit, VisitAdmin)
# admin_site.register(Point, PointAdmin)
# admin_site.register(User, UserAdmin)

urlpatterns = [
    # path('admin/', admin_site.urls),
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path("", include(static_urlpatterns)),
]
