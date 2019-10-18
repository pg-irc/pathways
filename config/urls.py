from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from main.version import VersionView
from human_services.organizations.viewsets import OrganizationViewSet
from human_services.locations.viewsets import (LocationViewSet, LocationViewSetUnderOrganizations)
from human_services.services_at_location.viewsets import ServiceAtLocationViewSet
from human_services.services.viewsets import ServiceViewSet, ServiceTopicsViewSet
from search.viewsets import RelatedTopicsViewSet, RelatedServicesViewSet
from qa_tool.viewsets import AlgorithmViewSet, RelevancyScoreViewSet
from rest_framework import routers
from config import documentation
from bc211.views import Bc211VersionView


def build_router():
    router = routers.DefaultRouter()

    router.register(r'organizations', OrganizationViewSet, base_name='organization')
    router.register(r'organizations/(?P<organization_id>[\w-]+)/locations',
                    LocationViewSetUnderOrganizations, base_name='organization-location')
    router.register(r'organizations/(?P<organization_id>[\w-]+)/services', ServiceViewSet, base_name='service')
    router.register(r'organizations/(?P<organization_id>[\w-]+)/locations/(?P<location_id>[\w-]+)/services',
                    ServiceViewSet, base_name='service')
    router.register(r'services', ServiceViewSet, base_name='service')
    router.register(r'services/(?P<service_id>[\w-]+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'services/(?P<service_id>[\w-]+)/locations/(?P<location_id>[\w-]+)/services_at_location',
                    ServiceAtLocationViewSet)
    router.register(r'services/(?P<service_id>[\w-]+)/related_topics', ServiceTopicsViewSet, base_name='topics')
    router.register(r'locations', LocationViewSet, base_name='location')
    router.register(r'locations/(?P<location_id>[\w-]+)/services', ServiceViewSet, base_name='service')
    router.register(r'locations/(?P<location_id>[\w-]+)/organizations/(?P<organization_id>[\w-]+)/services',
                    ServiceViewSet, base_name='service')
    router.register(r'locations/(?P<location_id>[\w-]+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'locations/(?P<location_id>[\w-]+)/services/(?P<service_id>[\w-]+)/services_at_location',
                    ServiceAtLocationViewSet)
    router.register(r'services_at_location', ServiceAtLocationViewSet, base_name='services_at_location')
    router.register(r'topics/(?P<topic_id>[\w-]+)/related_topics', RelatedTopicsViewSet, base_name='topics')
    router.register(r'topics/(?P<topic_id>[\w-]+)/related_services', RelatedServicesViewSet, base_name='topics')
    router.register(r'algorithms', AlgorithmViewSet, base_name='algorithms')
    router.register(r'algorithms/(?P<algorithm_id>[\w-]+)/relevancyscores',
                    RelevancyScoreViewSet, base_name='relevancyscores')

    return router


SCHEMA_VIEW = documentation.build_schema_view()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^version/$', VersionView.as_view(), name='version'),
    url(r'^bc211version/$', Bc211VersionView.as_view(), name='bc211_version'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('users.urls')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^swagger(?P<format>.json|.yaml)$', SCHEMA_VIEW.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', SCHEMA_VIEW.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', SCHEMA_VIEW.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

    url(r'^v1/', include(build_router().urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
