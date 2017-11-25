from django.conf.urls import url, include
from django.contrib import admin
from organizations.viewsets import OrganizationViewSet
from locations.viewsets import LocationViewSet, LocationViewSetUnderOrganizations
from rest_framework import routers

def build_router():
    router = routers.DefaultRouter()
    router.register(r'^organizations', OrganizationViewSet)
    router.register(r'^organizations/(?P<organization_id>[0-9a-zA-Z_]+)/locations', LocationViewSetUnderOrganizations, 'location')
    router.register(r'^locations', LocationViewSet, 'location')
    return router

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^v1/', include(build_router().urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^v0/forms/polls/', include('polls.web.urls')),
    url(r'^v0/polls/', include('polls.web.api')),
]
