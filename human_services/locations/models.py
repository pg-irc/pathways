from django.contrib.gis.db import models
from django.core import validators
from parler.models import TranslatableModel, TranslatedFields
from human_services.organizations.models import Organization
from human_services.addresses.models import Address, AddressType
from human_services.services.models import Service
from common.models import ValidateOnSaveMixin, RequiredCharField


class Location(ValidateOnSaveMixin, TranslatableModel):
    id = RequiredCharField(primary_key=True,
                           max_length=200,
                           validators=[validators.validate_slug])
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    services = models.ManyToManyField(Service,
                                      related_name='locations',
                                      through='ServiceAtLocation')
    point = models.PointField(blank=True, null=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        alternate_name=models.CharField(blank=True, null=True, max_length=200),
        description=models.TextField(blank=True, null=True)
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class ServiceAtLocation(ValidateOnSaveMixin, models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '"{service}" at "{location}"'.format(
            service=self.service,
            location=self.location
        )


class LocationAddress(ValidateOnSaveMixin, models.Model):
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 related_name='location_addresses')
    address_type = models.ForeignKey(AddressType, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('location', 'address_type')


    def __str__(self):
        return '"{address}" for "{location}"'.format(
            address=self.address,
            location=self.location
        )
