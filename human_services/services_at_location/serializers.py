from rest_framework import serializers
from human_services.locations import models
from human_services.services.serializers import ServiceSerializer
from human_services.locations.serializers import LocationSerializer


class ServiceAtLocationSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    location = LocationSerializer()

    class Meta:
        model = models.ServiceAtLocation
        fields = ('service', 'location')
