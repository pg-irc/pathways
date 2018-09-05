from rest_framework import serializers
from human_services.phone_numbers import models
from phonenumber_field.serializerfields import PhoneNumberField

class PhoneNumberSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField()

    class Meta:
        model = models.PhoneNumber
        fields = ('phone_number_type', 'phone_number')

