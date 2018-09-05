from rest_framework import serializers
from human_services.locations import models
from human_services.addresses.serializers import AddressSerializer
from human_services.phone_numbers.serializers import PhoneNumberSerializer


class LocationAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = models.LocationAddress
        fields = ('address_type', 'address')


class LocationSerializer(serializers.ModelSerializer):
    latitude = serializers.ReadOnlyField(source='point.x')
    longitude = serializers.ReadOnlyField(source='point.y')
    addresses = LocationAddressSerializer(source='location_addresses', many=True)
    phone_numbers = PhoneNumberSerializer(many=True)

    class Meta:
        model = models.Location
        fields = ('id', 'name', 'organization_id', 'latitude',
                  'longitude', 'description', 'addresses', 'phone_numbers')
