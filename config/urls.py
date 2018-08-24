from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from wagtail.wagtailadmin import urls as content_admin_urls
from wagtail.wagtaildocs import urls as content_documentation_urls
from wagtail.wagtailcore import urls as content_urls

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.wagtailimages.api.v2.endpoints import ImagesAPIEndpoint
from wagtail.wagtaildocs.api.v2.endpoints import DocumentsAPIEndpoint

from human_services.organizations.viewsets import OrganizationViewSet
from human_services.locations.viewsets import (LocationViewSet, LocationViewSetUnderOrganizations)
from human_services.services_at_location.viewsets import ServiceAtLocationViewSet
from human_services.services.viewsets import ServiceViewSet
from rest_framework import routers
from config import documentation

def build_api_router():
    router = routers.DefaultRouter()

    router.register(r'organizations', OrganizationViewSet, base_name='organization')
    router.register(r'organizations/(?P<organization_id>\w+)/locations',
                    LocationViewSetUnderOrganizations, base_name='organization-location')
    router.register(r'organizations/(?P<organization_id>\w+)/services', ServiceViewSet, base_name='service')
    router.register(r'organizations/(?P<organization_id>\w+)/locations/(?P<location_id>\w+)/services', ServiceViewSet, base_name='service')
    router.register(r'services', ServiceViewSet, base_name='service')
    router.register(r'services/(?P<service_id>\w+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'services/(?P<service_id>\w+)/locations/(?P<location_id>\w+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'locations', LocationViewSet, base_name='location')
    router.register(r'locations/(?P<location_id>\w+)/services', ServiceViewSet, base_name='service')
    router.register(r'locations/(?P<location_id>\w+)/organizations/(?P<organization_id>\w+)/services', ServiceViewSet, base_name='service')
    router.register(r'locations/(?P<location_id>\w+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'locations/(?P<location_id>\w+)/services/(?P<service_id>\w+)/services_at_location', ServiceAtLocationViewSet)
    router.register(r'services_at_location', ServiceAtLocationViewSet, base_name='services_at_location')

    return router

def build_cms_router():
    api_router = WagtailAPIRouter('wagtailapi')
    api_router.register_endpoint('pages', PagesAPIEndpoint)
    api_router.register_endpoint('images', ImagesAPIEndpoint)
    api_router.register_endpoint('documents', DocumentsAPIEndpoint)
    return api_router

SCHEMA_VIEW = documentation.build_schema_view()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # api docs
    url(r'^documentation/swagger(?P<format>.json|.yaml)$', SCHEMA_VIEW.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^documentation/swagger/$', SCHEMA_VIEW.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^documentation/redoc/$', SCHEMA_VIEW.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

    # content
    url(r'^content/admin/', include(content_admin_urls)),
    url(r'^content/documentation/', include(content_documentation_urls)), # this is not working
    url(r'^content/', include(content_urls)),

    # api
    url(r'^v1/content/', build_cms_router().urls),
    url(r'^v1/', include(build_api_router().urls)),

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
