from rest_framework import serializers
from locations import models

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'name', 'organization_id', 'latitude', 'longitude', 'description')
