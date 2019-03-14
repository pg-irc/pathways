from rest_framework import viewsets
from django.utils.decorators import method_decorator
from human_services.locations import models
from human_services.services_at_location import documentation, serializers
# TODO move common.filters to human_services.filters,
# LocationIdFilter and similar should be with the location code
from common.filters import (ProximityFilter, ProximityCutoffFilter, SearchFilter, LocationIdFilter,
                            ServiceIdFilter, TaxonomyFilter, ServiceSimilarityFilter)


# pylint: disable=too-many-ancestors
@method_decorator(name='list', decorator=documentation.get_service_at_location_list_schema())
class ServiceAtLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (models.ServiceAtLocation.objects.
                select_related('service').
                select_related('location').
                prefetch_related('service__translations').
                prefetch_related('service__organization').
                prefetch_related('location__translations').
                prefetch_related('location__location_addresses__address').
                prefetch_related('location__phone_numbers'))
    serializer_class = serializers.ServiceAtLocationSerializer
    search_fields = ('location__translations__name', 'location__translations__description',
                     'service__translations__name', 'service__translations__description')
    filter_backends = (ServiceSimilarityFilter,
                       SearchFilter,
                       LocationIdFilter,
                       ProximityFilter,
                       ProximityCutoffFilter,
                       ServiceIdFilter,
                       TaxonomyFilter,

                       )
