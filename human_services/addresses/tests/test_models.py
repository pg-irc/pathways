from copy import copy
from django.test import TestCase
from django.core import exceptions
from common.testhelpers.random_test_values import a_string
from common.testhelpers.database import validate_save_and_reload
from human_services.addresses.tests.helpers import AddressBuilder
from human_services.addresses.models import Address


class TestAddressModel(TestCase):

    def test_has_address_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.address, address.address)

    def test_address_field_cannot_be_empty(self):
        with self.assertRaises(exceptions.ValidationError):
            AddressBuilder().with_address('').create()

    def test_has_city_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.city, address.city)

    def test_city_field_cannot_be_empty(self):
        with self.assertRaises(exceptions.ValidationError):
            AddressBuilder().with_city('').create()

    def test_has_country_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.country, address.country)

    def test_country_field_cannot_be_empty(self):
        with self.assertRaises(exceptions.ValidationError):
            AddressBuilder().with_country('').create()

    def test_country_fields_cannot_exceed_two_characters(self):
        three_character_string = a_string(3)
        address = AddressBuilder().with_country(three_character_string).build()
        with self.assertRaises(exceptions.ValidationError):
            validate_save_and_reload(address)

    def test_has_attention_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.attention, address.attention)

    def test_empty_attention_field_saves_as_null(self):
        AddressBuilder().with_attention('').create()
        self.assertTrue(Address.objects.first().attention is None)

    def test_has_state_province_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.state_province, address.state_province)

    def test_empty_state_province_field_saves_as_null(self):
        AddressBuilder().with_state_province('').create()
        self.assertTrue(Address.objects.first().state_province is None)

    def test_has_postal_code_field(self):
        address = AddressBuilder().build()
        address_from_db = validate_save_and_reload(address)
        self.assertEqual(address_from_db.postal_code, address.postal_code)

    def test_empty_postal_code_field_saves_as_null(self):
        AddressBuilder().with_postal_code('').create()
        self.assertTrue(Address.objects.first().postal_code is None)

    def test_does_not_allow_duplicate_addresses(self):
        address = AddressBuilder().build()
        address_copy = copy(address)
        address.save()
        with self.assertRaises(exceptions.ValidationError):
            address_copy.save()
