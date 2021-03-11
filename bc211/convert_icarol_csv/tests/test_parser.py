import logging
import string
from django.test import TestCase
from common.testhelpers.random_test_values import (a_latitude, a_longitude, a_phone_number, a_string,
                                                   a_website_address, an_email_address, an_integer)
from bc211.convert_icarol_csv.tests.helpers import Bc211CsvDataBuilder, TestDataSink
from bc211.convert_icarol_csv.parser import CsvMissingIdParseException, parse, phone_header_with_index_one
logging.disable(logging.ERROR)


# TODO test that entities are unique accross organizations
# TODO test unicode characters


class ParseOrganizationsTests(TestCase):
    def test_can_parse_organization_id(self):
        the_id = a_string()
        data = Bc211CsvDataBuilder().as_organization().with_field('ResourceAgencyNum', the_id).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['id'], the_id)

    def test_can_parse_organization_name(self):
        the_name = a_string()
        data = Bc211CsvDataBuilder().as_organization().with_field('PublicName', the_name).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['name'], the_name)

    def test_can_parse_organization_alternate_name(self):
        the_alternate_name = a_string()
        data = Bc211CsvDataBuilder().as_organization().with_field('AlternateName', the_alternate_name).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['alternate_name'], the_alternate_name)

    def test_can_parse_description(self):
        the_description = a_string()
        data = Bc211CsvDataBuilder().as_organization().with_field('AgencyDescription', the_description).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['description'], the_description)

    def test_can_parse_email(self):
        the_email = an_email_address()
        data = Bc211CsvDataBuilder().as_organization().with_field('EmailAddressMain', the_email).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['email'], the_email)

    def test_can_parse_url(self):
        the_url = a_website_address()
        data = Bc211CsvDataBuilder().as_organization().with_field('WebsiteAddress', the_url).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['url'], the_url)

    def test_parse_as_organization_if_parent_agency_is_zero(self):
        parent_id = '0'
        the_id = str(an_integer(min=1))
        data = (Bc211CsvDataBuilder().
                with_field('ResourceAgencyNum', the_id).
                with_field('ParentAgencyNum', parent_id).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_organization()['id'], the_id)

    def test_can_parse_two_organizations(self):
        first_name = a_string()
        second_name = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('PublicName', first_name).next_row().
                as_organization().with_field('PublicName', second_name).build())
        parsed_data = parse(TestDataSink(), data).organizations
        self.assertEqual(parsed_data[0]['name'], first_name)
        self.assertEqual(parsed_data[1]['name'], second_name)

    def test_records_with_status_inactive_are_marked(self):
        data = (Bc211CsvDataBuilder().as_organization().with_field('AgencyStatus', 'Inactive').build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 1)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0')

    def test_records_with_description_marked_inactive_are_not_changed(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('AgencyDescription', 'DEL bla bla').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 1)
        self.assertEqual(parsed_data.organizations[0]['description'], 'DEL bla bla')

    def test_records_with_description_marked_inactive_are_not_changed_also_with_other_inactivating_field(self):
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('AgencyDescription', 'DEL bla bla').
                with_field('AgencyStatus', 'Inactive').build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 1)
        self.assertEqual(parsed_data.organizations[0]['description'], 'DEL bla bla')

    def test_records_with_province_YT_are_marked_as_inactive(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('MailingStateProvince', 'YT').next_row().
                as_organization().with_field('PhysicalStateProvince', 'YT').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0 ')
        self.assertRegex(parsed_data.organizations[1]['description'], r'^DEL0')

    def test_records_with_province_WA_are_marked_as_inactive(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('MailingStateProvince', 'WA').next_row().
                as_organization().with_field('PhysicalStateProvince', 'WA').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0')
        self.assertRegex(parsed_data.organizations[1]['description'], r'^DEL0')

    def test_records_with_province_WI_are_not_converted(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('MailingStateProvince', 'WI').next_row().
                as_organization().with_field('PhysicalStateProvince', 'WI').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0')
        self.assertRegex(parsed_data.organizations[1]['description'], r'^DEL0')

    def test_records_with_province_TX_are_marked_as_inactive(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('MailingStateProvince', 'TX').next_row().
                as_organization().with_field('PhysicalStateProvince', 'TX').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0')
        self.assertRegex(parsed_data.organizations[1]['description'], r'^DEL0')

    def test_records_with_province_TN_are_marked_as_inactive(self):
        data = (Bc211CsvDataBuilder().
                as_organization().with_field('MailingStateProvince', 'TN').next_row().
                as_organization().with_field('PhysicalStateProvince', 'TN').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertRegex(parsed_data.organizations[0]['description'], r'^DEL0')
        self.assertRegex(parsed_data.organizations[1]['description'], r'^DEL0')


class ParseServicesTests(TestCase):
    def test_parse_as_service_if_parent_agency_is_not_zero(self):
        parent_id = str(an_integer(min=1))
        the_id = str(an_integer(min=1))
        data = (Bc211CsvDataBuilder().
                with_field('ResourceAgencyNum', the_id).
                with_field('ParentAgencyNum', parent_id).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_service()['id'], the_id)

    def test_can_parse_last_verified_date_time(self):
        a_date = '9/15/2018 15:53'
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('LastVerifiedOn', a_date).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_service()['last_verified_on-x'], '2018-09-15')

    def test_can_parse_last_verified_date(self):
        a_date = '9/15/2018'
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('LastVerifiedOn', a_date).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_service()['last_verified_on-x'], '2018-09-15')

    def test_can_parse_alternative_date_format(self):
        a_date = '2018-09-15 0:00'
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('LastVerifiedOn', a_date).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_service()['last_verified_on-x'], '2018-09-15')

    def test_last_verified_date_can_be_empty(self):
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('LastVerifiedOn', '').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertIsNone(parsed_data.first_service()['last_verified_on-x'])

    def test_if_id_is_missing_throw_error(self):
        data = (Bc211CsvDataBuilder().
                with_field('ResourceAgencyNum', '').
                with_field('ParentAgencyNum', a_string()).
                build())
        with self.assertRaises(CsvMissingIdParseException):
            parse(TestDataSink(), data)


class ParsePhoneNumbersTests(TestCase):
    def test_default_phone_number_type(self):
        n = an_integer(min=1, max=5)
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field(f'Phone{n}Number', a_phone_number()).
                with_field(f'Phone{n}Type', '').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_phone_number()['type'], f'Phone {n}')

    def test_can_parse_organization_phone_number(self):
        the_number = a_phone_number()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Phone1Number', the_number).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_phone_number()['number'], the_number)

    def test_can_parse_organization_phone_number_type(self):
        the_type = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Phone1Type', the_type).
                with_field('Phone1Number', a_phone_number()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_phone_number()['type'], the_type)

    def test_can_parse_organization_phone_number_description(self):
        the_phone_description = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Phone1Name', the_phone_description).
                with_field('Phone1Number', a_phone_number()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_phone_number()['description'], the_phone_description)

    def test_set_index_on_phone_number_field_to_one(self):
        self.assertEqual(phone_header_with_index_one('Phone1Number'), 'Phone1Number')
        self.assertEqual(phone_header_with_index_one('Phone2Number'), 'Phone1Number')
        self.assertEqual(phone_header_with_index_one('Phone2Type'), 'Phone1Type')
        self.assertEqual(phone_header_with_index_one('PhoneXNumber'), 'PhoneXNumber')

    def test_can_parse_second_phone_number(self):
        first_number = a_phone_number()
        second_number = a_phone_number()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Phone1Number', first_number).
                with_field('Phone2Number', second_number).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.phone_numbers[0]['number'], first_number)
        self.assertEqual(parsed_data.phone_numbers[1]['number'], second_number)

    def test_can_parse_fax_number(self):
        a_number = a_phone_number()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('PhoneFax', a_number).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.phone_numbers), 1)
        self.assertEqual(parsed_data.phone_numbers[0]['number'], a_number)

    def test_sets_number_type_to_fax_for_fax_numbers(self):
        first_type = a_string()
        second_type = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Phone1Number', a_phone_number()).
                with_field('Phone1Type', first_type).
                with_field('Phone2Number', a_phone_number()).
                with_field('Phone2Type', second_type).
                with_field('PhoneFax', a_phone_number()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.phone_numbers), 3)
        self.assertEqual(parsed_data.phone_numbers[0]['type'], first_type)
        self.assertEqual(parsed_data.phone_numbers[1]['type'], second_type)
        self.assertEqual(parsed_data.phone_numbers[2]['type'], 'Fax')

    def test_leaves_out_phone_numbers_with_no_values(self):
        data = Bc211CsvDataBuilder().as_organization().with_field('Phone1Number', '').build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.phone_numbers), 0)


class ParseLocationsTests(TestCase):
    def test_parses_organization_name_as_location_name(self):
        the_name = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('PublicName', the_name).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_location()['name'], the_name)

    def test_parses_organization_alternate_name_as_location_name(self):
        the_alternate_name = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('AlternateName', the_alternate_name).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_location()['alternate_name'], the_alternate_name)

    def test_parse_location_latitude(self):
        the_latitude = a_latitude()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Latitude', str(the_latitude)).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_location()['latitude'], the_latitude)

    def test_parse_location_longitude(self):
        the_longitude = a_longitude()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('Longitude', str(the_longitude)).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_location()['longitude'], the_longitude)


class ParseCompleteRecordTests(TestCase):
    def setUp(self):
        self.the_organization_id = a_string()
        self.the_organization_name = a_string()
        self.the_alternate_name = a_string()
        self.the_description = a_string()
        self.the_email = an_email_address()
        self.the_url = a_website_address()
        self.the_number = a_phone_number()
        self.the_type = a_string()
        self.the_phone_description = a_string()
        self.the_latitude = a_latitude()
        self.the_longitude = a_longitude()
        self.the_address_line = a_string()
        self.the_city_line = a_string()
        self.the_province = a_string()
        self.the_postal_code = a_string()
        self.the_country = a_string()
        self.the_first_service_id = a_string()
        self.the_first_service_name = a_string()
        self.the_first_service_address = a_string()
        self.the_first_service_phone_number = a_phone_number()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', self.the_organization_id).
                with_field('PublicName', self.the_organization_name).
                with_field('AlternateName', self.the_alternate_name).
                with_field('AgencyDescription', self.the_description).
                with_field('EmailAddressMain', self.the_email).
                with_field('WebsiteAddress', self.the_url).
                with_field('Phone1Number', self.the_number).
                with_field('Phone1Type', self.the_type).
                with_field('Phone1Name', self.the_phone_description).
                with_field('Latitude', str(self.the_latitude)).
                with_field('Longitude', str(self.the_longitude)).
                with_field('MailingAddress1', self.the_address_line).
                with_field('MailingCity', self.the_city_line).
                with_field('MailingStateProvince', self.the_province).
                with_field('MailingPostalCode', self.the_postal_code).
                with_field('MailingCountry', self.the_country).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', self.the_first_service_id).
                with_field('ParentAgencyNum', self.the_organization_id).
                with_field('PublicName', self.the_first_service_name).
                with_field('MailingAddress1', self.the_first_service_address).
                with_field('Phone1Number', self.the_first_service_phone_number).
                build())
        self.parsed_data = parse(TestDataSink(), data)

    def test_organization_fields(self):
        self.assertEqual(len(self.parsed_data.organizations), 1)
        self.assertEqual(self.parsed_data.first_organization()['id'], self.the_organization_id)
        self.assertEqual(self.parsed_data.first_organization()['name'], self.the_organization_name)
        self.assertEqual(self.parsed_data.first_organization()['alternate_name'], self.the_alternate_name)
        self.assertEqual(self.parsed_data.first_organization()['description'], self.the_description)
        self.assertEqual(self.parsed_data.first_organization()['email'], self.the_email)
        self.assertEqual(self.parsed_data.first_organization()['url'], self.the_url)

    def test_service_fields(self):
        self.assertEqual(len(self.parsed_data.services), 1)
        self.assertEqual(self.parsed_data.first_service()['id'], self.the_first_service_id)

    def test_phone_number_fields(self):
        self.assertEqual(len(self.parsed_data.phone_numbers), 2)
        self.assertEqual(self.parsed_data.first_phone_number()['number'], self.the_number)
        self.assertEqual(self.parsed_data.first_phone_number()['type'], self.the_type)
        self.assertEqual(self.parsed_data.first_phone_number()['description'], self.the_phone_description)

    def test_location_fields(self):
        self.assertEqual(len(self.parsed_data.locations), 2)
        self.assertEqual(self.parsed_data.first_location()['organization_id'], self.the_organization_id)
        self.assertEqual(self.parsed_data.first_location()['name'], self.the_organization_name)
        self.assertEqual(self.parsed_data.first_location()['alternate_name'], self.the_alternate_name)
        self.assertEqual(self.parsed_data.first_location()['latitude'], self.the_latitude)
        self.assertEqual(self.parsed_data.first_location()['longitude'], self.the_longitude)

    def test_address_fields(self):
        self.assertEqual(len(self.parsed_data.addresses), 2)
        self.assertEqual(self.parsed_data.first_address()['address_1'], self.the_address_line)
        self.assertEqual(self.parsed_data.first_address()['city'], self.the_city_line)
        self.assertEqual(self.parsed_data.first_address()['state_province'], self.the_province)
        self.assertEqual(self.parsed_data.first_address()['postal_code'], self.the_postal_code)
        self.assertEqual(self.parsed_data.first_address()['country'], self.the_country)

    def test_synthetic_keys_are_not_empty(self):
        self.assertGreater(len(self.parsed_data.first_phone_number()['id']), 0)
        self.assertGreater(len(self.parsed_data.first_address()['id']), 0)
        self.assertGreater(len(self.parsed_data.services_at_location[0]['id']), 0)


class ParseTaxonomyTests(TestCase):
    def test_parse_taxonomy_term(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_term)

    def test_parse_taxonomy_term_with_space(self):
        the_term = 'Fire Services; Fire Stations'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 2)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'fire-services')
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], 'fire-stations')

    def test_parse_second_taxonomy_term_column(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerms', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_term)

    def test_parse_third_taxonomy_term_column(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTermsNotDeactivated', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_term)

    def test_parse_airs_taxonomy_term_column(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyCodes', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_term)

    def test_can_pass_in_vocabulary_to_parser(self):
        the_vocabulary = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyCodes', a_string()).build())
        parsed_data = parse(TestDataSink(), data, the_vocabulary)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], the_vocabulary)

    def test_does_not_split_airs_taxonomy_names_on_dash_or_dot(self):
        the_term = 'TA-3001.0750 * YB-9502.3300; TA-3003.0750 * YB-9504.1500;'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyCodes', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 4)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'TA-3001.0750')
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], 'YB-9502.3300')
        self.assertEqual(parsed_data.taxonomy_terms[2]['name'], 'TA-3003.0750')
        self.assertEqual(parsed_data.taxonomy_terms[3]['name'], 'YB-9504.1500')

    def test_split_taxonomy_terms_on_semicolon(self):
        the_term = 'one ; two ; three'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyCodes', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 3)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'one')
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], 'two')
        self.assertEqual(parsed_data.taxonomy_terms[2]['name'], 'three')

    def test_do_not_split_taxonomy_terms_on_space(self):
        the_term = 'one two three'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'one-two-three')

    def test_do_not_split_taxonomy_terms_on_slash(self):
        the_term = 'one/two/three'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'one-two-three')

    def test_use_the_leaf_node_of_hierarchical_taxonomy_terms(self):
        the_term = 'root - node1 - node 2 - leaf'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'leaf')

    def test_handle_two_hierarchical_terms(self):
        the_term = 'root - node1 - leaf1 ; root - node 2 - leaf2'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 2)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'leaf1')
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], 'leaf2')

    def test_change_terms_to_lower_case(self):
        the_term = 'One TWO three'
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], 'one-two-three')

    def test_strip_trailing_semicolon(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term + ';').build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_term)

    def test_split_two_terms(self):
        the_first_term = a_string()
        the_second_term = a_string()
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('TaxonomyTerm', the_first_term + '; ' + the_second_term + '; ').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 2)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_first_term)
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], the_second_term)

    def test_split_on_star(self):
        the_first_term = a_string()
        the_second_term = a_string()
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('TaxonomyTerm', the_first_term + ' * ' + the_second_term + ';').
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 2)
        self.assertEqual(parsed_data.taxonomy_terms[0]['name'], the_first_term)
        self.assertEqual(parsed_data.taxonomy_terms[1]['name'], the_second_term)

    def test_all_upper_case_term_in_TaxonomyTerm_column_is_part_of_taxonomy_called_bc211_what(self):
        the_term = a_string(from_character_string=string.ascii_uppercase)
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-what')

    def test_all_upper_case_term_in_TaxonomyTerms_column_is_part_of_taxonomy_called_bc211_what(self):
        the_term = a_string(from_character_string=string.ascii_uppercase)
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerms', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-what')

    def test_all_upper_case_term_in_TaxonomyTermsNotDeactivated_column_is_part_of_taxonomy_called_bc211_what(self):
        the_term = a_string(from_character_string=string.ascii_uppercase)
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTermsNotDeactivated', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-what')

    def test_all_lower_case_term_is_part_of_taxonomy_called_bc211_why(self):
        the_term = a_string(from_character_string=string.ascii_lowercase)
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerms', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-why')

    def test_all_first_letter_capitalized_is_part_of_taxonomy_called_bc211_who(self):
        head = a_string(length=1, from_character_string=string.ascii_uppercase)
        tail = a_string(from_character_string=string.ascii_lowercase)
        the_term = head + tail
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerms', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-who')

    def test_term_from_TaxonomyCodes_column_is_part_of_taxonomy_called_airs(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyCodes', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['vocabulary'], 'AIRS')

    def test_set_parent_name_to_empty_string(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['parent_name'], '')

    def test_set_parent_id_to_bc211(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.taxonomy_terms[0]['parent_id'], '')

    def test_compute_the_id(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertGreater(len(parsed_data.taxonomy_terms[0]['id']), 0)

    def test_does_not_save_duplicate_terms(self):
        the_term = a_string()
        data = (Bc211CsvDataBuilder().as_service().with_field('TaxonomyTerm', the_term + ';' + the_term).build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.taxonomy_terms), 1)

    def test_create_service_taxonomy_row_with_service_id(self):
        the_service_id = a_string()
        data = (Bc211CsvDataBuilder().
                as_service().
                with_field('ResourceAgencyNum', the_service_id).
                with_field('TaxonomyTerm', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.services_taxonomy), 1)
        self.assertEqual(parsed_data.services_taxonomy[0]['service_id'], the_service_id)

        the_taxonomy_term_id = parsed_data.taxonomy_terms[0]['id']
        self.assertEqual(parsed_data.services_taxonomy[0]['taxonomy_id'], the_taxonomy_term_id)

        self.assertGreater(len(parsed_data.services_taxonomy[0]['id']), 0)
        self.assertEqual(parsed_data.services_taxonomy[0]['taxonomy_detail'], '')


class AreTwoLocationsConsideredDuplicateTests(TestCase):
    def setUp(self):
        self.builder = (Bc211CsvDataBuilder().
                        as_organization().
                        with_field('ResourceAgencyNum', a_string()).
                        with_field('PublicName', a_string()).
                        with_field('AlternateName', a_string()).
                        with_field('AgencyDescription', a_string()).
                        with_field('EmailAddressMain', an_email_address()).
                        with_field('WebsiteAddress', a_website_address()).
                        with_field('Phone1Number', a_phone_number()).
                        with_field('Phone1Type', a_string()).
                        with_field('Phone1Name', a_string()).
                        with_field('Phone2Number', a_phone_number()).
                        with_field('Latitude', str(a_latitude())).
                        with_field('Longitude', str(a_longitude())).
                        with_field('MailingAddress1', a_string()).
                        with_field('MailingAddress2', a_string()).
                        with_field('MailingAddress3', a_string()).
                        with_field('MailingAddress4', a_string()).
                        with_field('MailingCity', a_string()).
                        with_field('MailingStateProvince', a_string()).
                        with_field('MailingPostalCode', a_string()).
                        with_field('MailingCountry', a_string()).
                        with_field('PhysicalAddress1', a_string()))

    def test_two_locations_with_different_organization_id_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('ResourceAgencyNum', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_public_names_id_are_not_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('PublicName', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 2)

    def test_two_locations_with_different_alternate_names_are_not_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('AlternateName', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 2)

    def test_two_locations_with_different_descriptions_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('AgencyDescription', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_latitude_are_not_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('Latitude', str(a_latitude())).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 2)

    def test_two_locations_with_different_longitudes_are_not_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('Longitude', str(a_longitude())).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 2)

    def test_two_locations_with_different_address_line_1_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingAddress1', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_address_line_2_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingAddress2', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_address_line_3_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingAddress3', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_address_line_4_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingAddress4', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_mailing_city_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingCity', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_province_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingStateProvince', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_postal_code_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingPostalCode', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_mailing_country_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('MailingCountry', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_physical_address_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('PhysicalAddress1', a_string()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_phone_number_are_not_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('Phone1Number', a_phone_number()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 2)

    def test_two_locations_with_different_phone_number_type_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('Phone1Type', a_phone_number()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)

    def test_two_locations_with_different_phone_number_names_are_duplicates(self):
        data = self.builder.duplicate_last_row().with_field('Phone1Name', a_phone_number()).build()
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 1)


class HumanServiceOneToManyRelationshipsTests(TestCase):
    def test_an_organization_with_two_locations(self):
        the_organization_id = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', the_organization_id).
                with_field('MailingAddress1', a_string()).
                with_field('MailingCity', a_string()).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', a_string()).
                with_field('ParentAgencyNum', the_organization_id).
                with_field('MailingAddress1', a_string()).
                with_field('MailingCity', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)

        self.assertEqual(len(parsed_data.locations), 1)
        self.assertEqual(parsed_data.locations[0]['organization_id'], the_organization_id)

    def test_an_organization_with_two_services(self):
        the_organization_id = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', the_organization_id).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', a_string()).
                with_field('ParentAgencyNum', the_organization_id).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', a_string()).
                with_field('ParentAgencyNum', the_organization_id).
                build())
        parsed_data = parse(TestDataSink(), data)

        self.assertEqual(len(parsed_data.services), 2)
        self.assertEqual(parsed_data.services[0]['organization_id'], the_organization_id)
        self.assertEqual(parsed_data.services[1]['organization_id'], the_organization_id)

    def test_location_with_two_services(self):
        the_organization_id = a_string()
        the_address_line = a_string()
        the_city_line = a_string()
        the_province = a_string()
        the_first_service_id = a_string()
        the_first_service_name = a_string()
        the_second_service_id = a_string()
        the_second_service_name = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', the_organization_id).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', the_first_service_id).
                with_field('PublicName', the_first_service_name).
                with_field('ParentAgencyNum', the_organization_id).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', the_second_service_id).
                with_field('PublicName', the_second_service_name).
                with_field('ParentAgencyNum', the_organization_id).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                build())
        parsed_data = parse(TestDataSink(), data)

        self.assertEqual(len(parsed_data.locations), 3)
        first_location_id = parsed_data.locations[1]['id']
        second_location_id = parsed_data.locations[2]['id']

        self.assertEqual(len(parsed_data.services_at_location), 2)
        self.assertEqual(parsed_data.services_at_location[0]['service_id'], the_first_service_id)
        self.assertEqual(parsed_data.services_at_location[1]['service_id'], the_second_service_id)
        self.assertEqual(parsed_data.services_at_location[0]['location_id'], first_location_id)
        self.assertEqual(parsed_data.services_at_location[1]['location_id'], second_location_id)

    def test_service_at_two_locations(self):
        the_organization_id = a_string()
        the_address_line = a_string()
        the_city_line = a_string()
        the_province = a_string()
        the_service_id = a_string()
        the_service_name = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', the_organization_id).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', the_service_id).
                with_field('PublicName', the_service_name).
                with_field('ParentAgencyNum', the_organization_id).
                # for the locations to count as different, the lat/long has to be different
                with_field('Latitude', a_latitude()).
                with_field('AgencyDescription', a_string()).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', the_service_id).
                with_field('PublicName', the_service_name).
                with_field('ParentAgencyNum', the_organization_id).
                with_field('Latitude', a_latitude()).
                with_field('AgencyDescription', a_string()).
                with_field('MailingAddress1', a_string()).
                with_field('MailingCity', a_string()).
                with_field('MailingStateProvince', a_string()).
                build())

        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.locations), 3)
        # location at offset 0 is for the organization
        first_location_id = parsed_data.locations[1]['id']
        second_location_id = parsed_data.locations[2]['id']

        self.assertEqual(len(parsed_data.services_at_location), 2)
        self.assertEqual(parsed_data.services_at_location[0]['service_id'], the_service_id)
        self.assertEqual(parsed_data.services_at_location[1]['service_id'], the_service_id)
        self.assertEqual(parsed_data.services_at_location[0]['location_id'], first_location_id)
        self.assertEqual(parsed_data.services_at_location[1]['location_id'], second_location_id)

    def test_a_location_can_have_five_phone_numbers(self):
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', a_string()).
                with_field('MailingAddress1', a_string()).
                with_field('Phone1Number', a_phone_number()).
                with_field('Phone1Type', a_string()).
                with_field('Phone2Number', a_phone_number()).
                with_field('Phone2Type', a_string()).
                with_field('Phone3Number', a_phone_number()).
                with_field('Phone3Type', a_string()).
                with_field('Phone4Number', a_phone_number()).
                with_field('Phone4Type', a_string()).
                with_field('Phone5Number', a_phone_number()).
                with_field('Phone5Type', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)

        self.assertEqual(len(parsed_data.phone_numbers), 5)
        the_location_id = parsed_data.first_location()['id']
        self.assertEqual(parsed_data.phone_numbers[0]['location_id'], the_location_id)
        self.assertEqual(parsed_data.phone_numbers[1]['location_id'], the_location_id)
        self.assertEqual(parsed_data.phone_numbers[2]['location_id'], the_location_id)
        self.assertEqual(parsed_data.phone_numbers[3]['location_id'], the_location_id)
        self.assertEqual(parsed_data.phone_numbers[4]['location_id'], the_location_id)

    def test_duplicate_phone_numbers_are_removed(self):
        the_phone_number = a_phone_number()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', a_string()).
                with_field('MailingAddress1', a_string()).
                with_field('Phone1Number', the_phone_number).
                with_field('Phone1Type', a_string()).
                with_field('Phone2Number', the_phone_number).
                with_field('Phone2Type', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)

        self.assertEqual(len(parsed_data.phone_numbers), 1)
        self.assertEqual(parsed_data.phone_numbers[0]['number'], the_phone_number)

    # two locations with the same phone number (for argument's sake) have two phone number records
    def test_one_location_with_postal_and_physical_address(self):
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', a_string()).
                with_field('PublicName', a_string()).
                with_field('AlternateName', a_string()).
                with_field('EmailAddressMain', an_email_address()).
                with_field('MailingAddress1', a_string()).
                with_field('MailingAddress2', a_string()).
                with_field('MailingAddress3', a_string()).
                with_field('MailingAddress4', a_string()).
                with_field('MailingCity', a_string()).
                with_field('MailingStateProvince', a_string()).
                with_field('MailingPostalCode', a_string()).
                with_field('MailingCountry', a_string()).
                with_field('PhysicalAddress1', a_string()).
                with_field('PhysicalAddress2', a_string()).
                with_field('PhysicalAddress3', a_string()).
                with_field('PhysicalAddress4', a_string()).
                with_field('PhysicalCity', a_string()).
                with_field('PhysicalStateProvince', a_string()).
                with_field('PhysicalPostalCode', a_string()).
                with_field('PhysicalCountry', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)
        the_location_id = parsed_data.locations[0]['id']

        self.assertEqual(len(parsed_data.addresses), 2)
        self.assertEqual(parsed_data.addresses[0]['location_id'], the_location_id)
        self.assertEqual(parsed_data.addresses[1]['location_id'], the_location_id)

    def test_two_locations_with_the_same_address(self):
        the_organization_id = a_string()
        the_address_line = a_string()
        the_city_line = a_string()
        the_province = a_string()
        the_postal_code = a_string()
        the_country = a_string()
        the_first_service_id = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('ResourceAgencyNum', the_organization_id).
                with_field('Latitude', str(a_latitude())).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                with_field('MailingPostalCode', the_postal_code).
                with_field('MailingCountry', the_country).
                next_row().
                as_service().
                with_field('ResourceAgencyNum', the_first_service_id).
                with_field('ParentAgencyNum', the_organization_id).
                with_field('Latitude', str(a_latitude())).
                with_field('MailingAddress1', the_address_line).
                with_field('MailingCity', the_city_line).
                with_field('MailingStateProvince', the_province).
                with_field('MailingPostalCode', the_postal_code).
                with_field('MailingCountry', the_country).
                build())
        parsed_data = parse(TestDataSink(), data)
        the_first_location_id = parsed_data.locations[0]['id']
        the_second_location_id = parsed_data.locations[1]['id']

        self.assertEqual(len(parsed_data.locations), 2)
        self.assertEqual(len(parsed_data.addresses), 2)
        self.assertNotEqual(parsed_data.addresses[0]['id'], parsed_data.addresses[1]['id'])
        self.assertEqual(parsed_data.addresses[0]['location_id'], the_first_location_id)
        self.assertEqual(parsed_data.addresses[1]['location_id'], the_second_location_id)
    # Phone numbers uniquely identified by their phone number field
    # Addresses uniquely identified by their address fields
    # Locations uniquely identified by their organization id, name, phone number ids and address ids


class ParseAddressTests(TestCase):
    def test_can_parse_address_line_one(self):
        the_address_line = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingAddress1', the_address_line).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['address_1'], the_address_line)

    def test_can_parse_remaining_address_lines(self):
        address_line_2 = a_string()
        address_line_3 = a_string()
        address_line_4 = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingAddress2', address_line_2).
                with_field('MailingAddress3', address_line_3).
                with_field('MailingAddress4', address_line_4).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['address_2'], address_line_2)
        self.assertEqual(parsed_data.first_address()['address_3'], address_line_3)
        self.assertEqual(parsed_data.first_address()['address_4'], address_line_4)

    def test_can_parse_address_city(self):
        the_city_line = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingCity', the_city_line).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['city'], the_city_line)

    def test_can_parse_address_state_province(self):
        the_province = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingStateProvince', the_province).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['state_province'], the_province)

    def test_can_parse_address_postal_code(self):
        the_postal_code = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingPostalCode', the_postal_code).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['postal_code'], the_postal_code)

    def test_can_parse_address_country(self):
        the_country = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingCountry', the_country).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['country'], the_country)

    def test_can_parse_physical_address(self):
        the_address_line = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('PhysicalAddress1', the_address_line).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['address_1'], the_address_line)

    def test_marks_physical_address_as_physical(self):
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('PhysicalAddress1', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['type'], 'physical_address')

    def test_marks_postal_address_as_postal(self):
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingAddress1', a_string()).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['type'], 'postal_address')

    def test_can_parse_both_physical_and_postal_address(self):
        the_physical_address_line = a_string()
        the_postal_address_line = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingAddress1', the_postal_address_line).
                with_field('PhysicalAddress1', the_physical_address_line).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(parsed_data.first_address()['address_1'], the_postal_address_line)
        self.assertEqual(parsed_data.second_address()['address_1'], the_physical_address_line)

    def test_can_have_same_address_as_physical_and_postal(self):
        the_address_line = a_string()
        data = (Bc211CsvDataBuilder().
                as_organization().
                with_field('MailingAddress1', the_address_line).
                with_field('PhysicalAddress1', the_address_line).
                build())
        parsed_data = parse(TestDataSink(), data)
        self.assertEqual(len(parsed_data.addresses), 2)
        self.assertEqual(parsed_data.first_address()['address_1'], the_address_line)
        self.assertEqual(parsed_data.second_address()['address_1'], the_address_line)
        self.assertEqual(parsed_data.first_address()['location_id'], parsed_data.second_address()['location_id'])
        self.assertNotEqual(parsed_data.first_address()['id'], parsed_data.second_address()['id'])
