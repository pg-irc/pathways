from rest_framework import viewsets
from locations import models, serializers

# pylint: disable=too-many-ancestors
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer

# pylint: disable=too-many-ancestors
class LocationViewSetUnderOrganizations(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        organization_id = self.kwargs['organization_id']
        return models.Location.objects.filter(organization=organization_id)

    serializer_class = serializers.LocationSerializer
