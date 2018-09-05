import unittest
from django.test import TestCase
from django.core import exceptions
from django.db import utils as django_utils
from human_services.services.tests.helpers import ServiceBuilder
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.locations.tests.helpers import LocationBuilder
from human_services.locations.models import ServiceAtLocation
from common.testhelpers.database import validate_save_and_reload


class TestServiceModel(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().build()
        self.organization.save()

    def test_has_id_field(self):
        service_id = 'the_id'
        service = ServiceBuilder(self.organization).with_id(service_id).build()
        service_from_db = validate_save_and_reload(service)
        self.assertEqual(service_from_db.id, service_id)

    def test_id_cannot_be_none(self):
        null_id = None
        service = ServiceBuilder(self.organization).with_id(null_id).build()
        with self.assertRaises(exceptions.ValidationError):
            service.full_clean()

    def test_id_cannot_be_empty(self):
        empty_id = ''
        service = ServiceBuilder(self.organization).with_id(empty_id).build()
        with self.assertRaises(exceptions.ValidationError):
            service.full_clean()

    def test_id_cannot_contain_space(self):
        service_id = 'the id'
        service = ServiceBuilder(self.organization).with_id(service_id).build()
        with self.assertRaises(exceptions.ValidationError):
            service.full_clean()

    def test_has_name(self):
        name = 'The service name'
        service = ServiceBuilder(self.organization).with_name(name).build()
        service_from_db = validate_save_and_reload(service)
        self.assertEqual(service_from_db.name, name)

    @unittest.expectedFailure
    def test_cannot_be_empty(self):
        name = ''
        service = ServiceBuilder(self.organization).with_name(name).build()
        with self.assertRaises(exceptions.ValidationError):
            service.full_clean()

    def test_name_cannot_be_none(self):
        null_name = None
        service = ServiceBuilder(self.organization).with_name(null_name).build()
        # Note that we're getting an integrity error from the database here,
        # haven't figured out how to make this fail validation which would be cleaner
        # and would also allow us invalidate on the empty string.
        with self.assertRaises(django_utils.IntegrityError):
            validate_save_and_reload(service)

    def test_can_set_description(self):
        description = 'The service description'
        service = ServiceBuilder(self.organization).with_description(description).build()
        service_from_db = validate_save_and_reload(service)
        self.assertEqual(service_from_db.description, description)

    def test_description_can_be_none(self):
        null_description = None
        service = ServiceBuilder(self.organization).with_description(null_description).build()
        service_from_db = validate_save_and_reload(service)
        self.assertEqual(service_from_db.description, null_description)

    @unittest.expectedFailure
    def test_empty_description_is_saved_as_null(self):
        empty_description = ''
        null_description = None
        service = ServiceBuilder(self.organization).with_description(empty_description).build()
        service_from_db = validate_save_and_reload(service)
        self.assertEqual(service_from_db.description, null_description)

    def test_description_is_multilingual(self):
        service = ServiceBuilder(self.organization).build()

        self.set_description_in_language(service, 'en', 'In English')
        self.set_description_in_language(service, 'fr', 'En français')
        service_from_db = validate_save_and_reload(service)

        self.assert_description_in_language_equals(service_from_db, 'en', 'In English')
        self.assert_description_in_language_equals(service_from_db, 'fr', 'En français')

    def test_has_locations_attribute(self):
        service = ServiceBuilder(self.organization).build()
        validate_save_and_reload(service)

        location = LocationBuilder(self.organization).build()
        validate_save_and_reload(location)

        service_at_location = ServiceAtLocation(service=service, location=location)
        validate_save_and_reload(service_at_location)

        self.assertEqual(service.locations.first(), location)

    # pylint: disable=invalid-name
    def test_locations_is_empty_if_no_service_location_exists(self):
        service = ServiceBuilder(self.organization).build()
        service_from_db = validate_save_and_reload(service)

        self.assertEqual(service_from_db.locations.count(), 0)

    def set_description_in_language(self, service, language, text):
        service.set_current_language(language)
        service.description = text

    def assert_description_in_language_equals(self, service, language, expected_text):
        service.set_current_language(language)
        self.assertEqual(service.description, expected_text)
