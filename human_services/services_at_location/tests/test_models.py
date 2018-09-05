from django.test import TestCase
from django.core import exceptions
from human_services.locations.tests.helpers import LocationBuilder
from human_services.locations.models import ServiceAtLocation
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from common.testhelpers.database import validate_save_and_reload


class TestServiceAtLocationModel(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().build()
        self.organization.save()

        self.service = ServiceBuilder(self.organization).build()
        self.service.save()

        self.location = LocationBuilder(self.organization).build()
        self.location.save()

    def test_has_service_field(self):
        service_at_location = ServiceAtLocation(service=self.service, location=self.location)
        service_location_from_db = validate_save_and_reload(service_at_location)
        self.assertEqual(service_location_from_db.service, self.service)

    def test_service_cannot_be_none(self):
        service_at_location = ServiceAtLocation(service=None, location=self.location)
        with self.assertRaises(exceptions.ValidationError):
            service_at_location.full_clean()

    def test_has_location_field(self):
        service_at_location = ServiceAtLocation(service=self.service, location=self.location)
        service_location_from_db = validate_save_and_reload(service_at_location)
        self.assertEqual(service_location_from_db.location, self.location)

    def test_location_cannot_be_none(self):
        service_at_location = ServiceAtLocation(service=self.service, location=None)
        with self.assertRaises(exceptions.ValidationError):
            service_at_location.full_clean()
