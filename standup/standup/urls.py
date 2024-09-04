# sourcery skip: aug-assign
"""
URL configuration for standup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

import agenda.urls
import dashboard.urls
import supportmail.urls

from django.contrib import admin
from agenda.models import SupportEngineer
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers, serializers, viewsets
from debug_toolbar.toolbar import debug_toolbar_urls




class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SupportEngineer
        fields = ["url", "username", "email", "is_staff"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = SupportEngineer.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path('admin/defender/', include('defender.urls')), # defender admin
    path('accounts/', include('allauth.urls')),
    path("admin/", admin.site.urls),
    path("support-mail", include(supportmail.urls)),
    path("api/", include(agenda.urls)),
    path("agenda", include(dashboard.urls)),
    re_path(r"^", include(dashboard.urls)),
    path("martor/", include("martor.urls")),
    re_path(r"^ht/", include("health_check.urls")),
    path('', include('django_prometheus.urls')),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + debug_toolbar_urls()