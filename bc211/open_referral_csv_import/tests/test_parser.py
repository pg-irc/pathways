from django.test import TestCase
from bc211.open_referral_csv_import import parser
from bc211.parser import remove_double_escaped_html_markup
from bc211.open_referral_csv_import import exceptions
from common.testhelpers.random_test_values import a_string, a_latitude


class LocationParserTests(TestCase):
    def test_can_parse_coordinate(self):
        the_latitude = a_latitude()
        parsed_latitude = parser.parse_coordinate_if_defined(str(the_latitude))
        self.assertEqual(parsed_latitude, the_latitude)

    def test_returns_none_if_coordinate_is_empty(self):
        empty_latitude = ''
        parsed_coordinate = parser.parse_coordinate_if_defined(empty_latitude)
        self.assertEqual(parsed_coordinate, None)


class AddressParserTests(TestCase):
    def test_can_parse_addresses_when_all_address_fields_are_not_empty(self):
        address_1 = a_string()
        address_2 = a_string()
        address_3 = a_string()
        address_4 = a_string()
        addresses = [address_1, address_2, address_3, address_4]
        parsed_addresses = parser.parse_addresses(addresses)
        self.assertEqual(f'{address_1}\n{address_2}\n{address_3}\n{address_4}', parsed_addresses)

    def test_can_parse_addresses_when_some_fields_are_empty(self):
        address_1 = a_string()
        address_2 = a_string()
        address_3 = ''
        address_4 = ''
        addresses = [address_1, address_2, address_3, address_4]
        parsed_addresses = parser.parse_addresses(addresses)
        self.assertEqual(f'{address_1}\n{address_2}', parsed_addresses)


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
        with self.assertRaises(exceptions.MissingRequiredFieldCsvParseException):
            parser.parse_required_field('id', None)

    def test_returns_empty_string_if_optional_field_is_missing(self):
        parsed_id = parser.parse_optional_field(None)
        self.assertEqual(parsed_id, '')

    def test_website_without_prefix_parsed_as_http(self):
        the_website = 'www.example.org'
        parsed_website = parser.parse_website_with_prefix(a_string(), the_website)
        self.assertEqual(parsed_website, 'http://www.example.org')

    def test_website_with_http_prefix_parsed_as_http(self):
        the_website = 'http://www.example.org'
        parsed_website = parser.parse_website_with_prefix(a_string(), the_website)
        self.assertEqual(parsed_website, 'http://www.example.org')

    def test_website_with_https_prefix_parsed_as_https(self):
        the_website = 'https://www.example.org'
        parsed_website = parser.parse_website_with_prefix(a_string(), the_website)
        self.assertEqual(parsed_website, 'https://www.example.org')

    def test_invalid_email_returns_None(self):
        the_email = 'vancouver@ami.ca?'
        parsed_email = parser.parse_email(a_string(), the_email)
        self.assertEqual(parsed_email, None)

    def test_invalid_website_returns_None(self):
        the_website = 'httpL//(none)'
        parsed_website = parser.parse_website_with_prefix(a_string(), the_website)
        self.assertEqual(parsed_website, None)

    def test_sets_canada_to_two_letter_country_code(self):
        country = 'Canada'
        parsed_country = parser.two_letter_country_code_or_none(country)
        self.assertEqual(parsed_country, 'CA')

    def test_sets_united_states_to_two_letter_country_code(self):
        country = 'United States'
        parsed_country = parser.two_letter_country_code_or_none(country)
        self.assertEqual(parsed_country, 'US')

    def test_raises_exception_when_country_is_invalid(self):
        with self.assertRaises(exceptions.InvalidFieldCsvParseException):
            parser.two_letter_country_code_or_none('All countries')
