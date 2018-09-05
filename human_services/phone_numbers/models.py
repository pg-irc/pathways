from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from common.models import RequiredCharField
from human_services.locations.models import Location


class PhoneNumberType(models.Model):
    id = RequiredCharField(primary_key=True, max_length=200)

class PhoneNumber(models.Model):
    location = models.ForeignKey(Location, related_name='phone_numbers')
    phone_number_type = models.ForeignKey(PhoneNumberType)
    phone_number = PhoneNumberField()
