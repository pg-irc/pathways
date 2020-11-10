import unittest
import string
from django.test import TestCase
from bc211.open_referral_csv_import.tests.helpers import OpenReferralCsvAddressBuilder
from ..address import parse_address
from bc211.open_referral_csv_import import parser
from common.testhelpers.random_test_values import (a_string, an_email_address, a_website_address,
                                                    a_latitude_as_a_string, a_longitude_as_a_string)
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from human_services.locations.tests.helpers import LocationBuilder
from bc211.parser import remove_double_escaped_html_markup
from bc211.open_referral_csv_import.exceptions import MissingRequiredFieldCsvParseException


class OpenReferralLocationParserTests(TestCase):
    def test_can_parse_latitude(self):
        the_latitude = a_latitude_as_a_string()
        parsed_latitude = parser.parse_coordinate_if_defined('latitude', the_latitude)
        self.assertEqual(parsed_latitude, float(the_latitude))

    def test_can_parse_longitude(self):
        the_longitude = a_longitude_as_a_string()
        parsed_longitude = parser.parse_coordinate_if_defined('longitude', the_longitude)
        self.assertEqual(parsed_longitude, float(the_longitude))


class OpenReferralAddressesParserTests(TestCase):
    def setUp(self):
        self.headers = ['id', 'type', 'location_id', 'attention', 'address_1', 'address_2', 'address_3', 'address_4', 'city',
                        'region', 'state_province', 'postal_code', 'country']
        organization = OrganizationBuilder().build()
        self.location_id_passed_to_location_builder = a_string()
        self.location = LocationBuilder(organization).with_id(self.location_id_passed_to_location_builder).build()
    
    def test_can_parse_type(self):
        the_type = 'postal_address'
        address_data = OpenReferralCsvAddressBuilder(self.location).with_address_type(the_type).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.type, the_type)

    def test_can_parse_location_id(self):
        address_data = OpenReferralCsvAddressBuilder(self.location).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.location_id, self.location_id_passed_to_location_builder)

    def test_can_parse_attention(self):
        the_attention = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_attention(the_attention).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.attention, the_attention)
    
    def test_can_parse_address(self):
        the_address = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_address(the_address).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.address, the_address)
    
    def test_can_parse_city(self):
        the_city = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_city(the_city).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.city, the_city)
    
    def test_can_parse_state_province(self):
        the_state_province = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_state_province(the_state_province).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.state_province, the_state_province)

    def test_can_parse_postal_code(self):
        the_postal_code = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_postal_code(the_postal_code).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.postal_code, the_postal_code)
    
    def test_can_parse_country(self):
        the_country = a_string(2, string.ascii_uppercase)
        address_data = OpenReferralCsvAddressBuilder(self.location).with_country(the_country).build()
        address = parse_address(self.headers, address_data)
        self.assertEqual(address.country, the_country)


class ParserHelperTests(TestCase):
    def test_removes_doubly_escaped_bold_markup_from_field(self):
        the_name = '&amp;lt;b&amp;gt;abc'
        html_markup = remove_double_escaped_html_markup(the_name)
        self.assertEqual(html_markup, 'abc')

    def test_removes_doubly_escaped_strong_markup_from_field(self):
        the_name = '&amp;lt;strong&amp;gt;abc'
        html_markup = remove_double_escaped_html_markup(the_name)
        self.assertEqual(html_markup, 'abc')

    def test_throws_when_required_field_is_missing(self):
        with self.assertRaises(MissingRequiredFieldCsvParseException):
            parser.parse_required_field('id', None)

    def test_returns_none_if_optional_field_is_missing(self):
        parsed_id = parser.parse_optional_field('id', None)
        self.assertEqual(parsed_id, None)

    def test_website_without_prefix_parsed_as_http(self):
        the_website = 'www.example.org'
        parsed_website = parser.parse_website_with_prefix('website', the_website)
        self.assertEqual(parsed_website, 'http://www.example.org')

    def test_website_with_http_prefix_parsed_as_http(self):
        the_website = 'http://www.example.org'
        parsed_website = parser.parse_website_with_prefix('website', the_website)
        self.assertEqual(parsed_website, 'http://www.example.org')

    def test_website_with_https_prefix_parsed_as_https(self):
        the_website = 'https://www.example.org'
        parsed_website = parser.parse_website_with_prefix('website', the_website)
        self.assertEqual(parsed_website, 'https://www.example.org')
    
    def test_returns_none_if_coordinate_is_empty(self):
        empty_latitude = ''
        foo = parser.parse_coordinate_if_defined('latitude', empty_latitude)
        self.assertEqual(foo, None)
