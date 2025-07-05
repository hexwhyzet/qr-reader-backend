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
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from myproject.settings import DEBUG
from users.views import ChangePasswordView, UserListAPIView

static_urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}),
] if DEBUG else []
urlpatterns = [
    # path('admin/', admin_site.urls),
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('tg_bot/', include('tg_bot.urls')),
    path('api/food/', include('food.urls')),
    path('api/dispatch/', include('dispatch.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/users/', UserListAPIView.as_view()),
    path('', include(static_urlpatterns)),
]
