import unittest
import logging
import xml.etree.ElementTree as etree
from common.testhelpers.random_test_values import a_string, a_phone_number

from bc211 import parser, dtos
from bc211.exceptions import MissingRequiredFieldXmlParseException

logging.disable(logging.ERROR)

REAL_211_DATA_SET = 'bc211/data/BC211_data_one_agency.xml'
MULTI_AGENCY__211_DATA_SET = 'bc211/data/BC211_data_excerpt.xml'
MINIMAL_211_DATA_SET = '''
<Source>
    <Agency>
        <Key>the agency key</Key>
        <Name>the agency name</Name>
        <AgencyDescription>the agency description</AgencyDescription>
        <URL>
            <Address>http://www.the-agency.org</Address>
        </URL>
        <Email>
            <Address>info@the-agency.org</Address>
        </Email>
        <Site>
            <Key>the site key</Key>
            <Name>the site name</Name>
            <SiteDescription>the site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
            <SiteService>
                <Key>the service key</Key>
                <Name>the service name</Name>
                <Description>the service description</Description>
            </SiteService>
            <SiteService>
                <Key>the second service key</Key>
                <Name>the second service name</Name>
                <Description>the second service description</Description>
            </SiteService>
            <MailingAddress>
                <Line1>Line1</Line1>
                <Line2>Line2</Line2>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </MailingAddress>
            <PhysicalAddress>
                <Line1>Line1</Line1>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </PhysicalAddress>
        </Site>
        <Site>
            <Key>the second site key</Key>
            <Name>the second site name</Name>
            <SiteDescription>the second site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
            <SiteService>
                <Key>the second site's service key</Key>
                <Name>the second site's service name</Name>
                <Description>the second site's service description</Description>
            </SiteService>
            <MailingAddress>
                <Line1>Line1</Line1>
                <Line2>Line2</Line2>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </MailingAddress>
            <PhysicalAddress>
                <Line1>Line1</Line1>
                <City>City</City>
                <Country>Country</Country>
                <State>State</State>
                <ZipCode>Code</ZipCode>
            </PhysicalAddress>
        </Site>
    </Agency>
</Source>'''


class BC211ParserTests(unittest.TestCase):
    def test_parse_many_locations(self):
        file_open_for_reading = open(MULTI_AGENCY__211_DATA_SET, 'r')
        xml = file_open_for_reading.read()
        organizations = list(parser.parse(xml))
        locations_from_first_organization = list(organizations[0].locations)
        services_from_first_location = list(locations_from_first_organization[0].services)
        taxonomy_terms_from_first_service = list(services_from_first_location[0].taxonomy_terms)
        addresses_from_first_location = [
            locations_from_first_organization[0].physical_address,
            locations_from_first_organization[0].postal_address
        ]
        self.assertEqual(len(organizations), 16)
        self.assertEqual(len(locations_from_first_organization), 1)
        self.assertEqual(len(services_from_first_location), 1)
        self.assertEqual(len(taxonomy_terms_from_first_service), 27)
        self.assertEqual(len(addresses_from_first_location), 2)


class OrganizationParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.from_real_data = parser.parse_agency(root.find('Agency'))

        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_agency(root.find('Agency'))

    def test_can_parse_id(self):
        self.assertEqual(self.from_real_data.id, '9487364')
        self.assertEqual(self.from_minimal_data.id, 'the agency key')

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the agency name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the agency description')

    def test_can_parse_website(self):
        self.assertEqual(self.from_real_data.website, 'http://www.langleycdc.com')
        self.assertEqual(self.from_minimal_data.website, 'http://www.the-agency.org')

    def test_website_without_prefix_parsed_as_http(self):
        xml = self.data_set_with_website('www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'http://www.the-agency.org')

    def test_website_with_http_prefix_parsed_as_http(self):
        xml = self.data_set_with_website('http://www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'http://www.the-agency.org')

    def test_website_with_https_prefix_parsed_as_https(self):
        xml = self.data_set_with_website('https://www.the-agency.org')
        website = self.get_website_as_parsed(xml)
        self.assertEqual(website, 'https://www.the-agency.org')

    def data_set_with_website(self, website):
        return MINIMAL_211_DATA_SET.replace('http://www.the-agency.org', website)

    def get_website_as_parsed(self, xml):
        root = etree.fromstring(xml)
        organization = parser.parse_agency(root.find('Agency'))
        return organization.website

    def test_can_parse_email(self):
        self.assertEqual(self.from_real_data.email, 'info@langleycdc.com')
        self.assertEqual(self.from_minimal_data.email, 'info@the-agency.org')

    def test_can_parse_locations_under_organization(self):
        self.assertEqual(len(list(self.from_real_data.locations)), 1)
        self.assertEqual(len(list(self.from_minimal_data.locations)), 2)


class LocationParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.organization_id_passed_to_parser = 'the organization id'
        self.from_real_data = parser.parse_site(root.find('Agency/Site'),
                                                self.organization_id_passed_to_parser)
        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_site(root.find('Agency/Site'),
                                                   self.organization_id_passed_to_parser)

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the site name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the site description')

    def test_can_parse_latitude(self):
        self.assertAlmostEqual(self.from_real_data.spatial_location.latitude, 49.087284)
        self.assertAlmostEqual(self.from_minimal_data.spatial_location.latitude, 123.456)

    def test_can_parse_longitude(self):
        self.assertAlmostEqual(self.from_real_data.spatial_location.longitude, -122.607918)
        self.assertAlmostEqual(self.from_minimal_data.spatial_location.longitude, -154.321)

    def test_sets_the_organization_id(self):
        self.assertEqual(self.from_real_data.organization_id,
                         self.organization_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.organization_id,
                         self.organization_id_passed_to_parser)


class ServiceParserTests(unittest.TestCase):
    def setUp(self):
        root = etree.fromstring(open(REAL_211_DATA_SET, 'r').read())
        self.organization_id_passed_to_parser = 'the organization id'
        self.site_id_passed_to_parser = 'the site id'
        self.from_real_data = parser.parse_service(
            root.find('Agency/Site/SiteService'),
            self.organization_id_passed_to_parser,
            self.site_id_passed_to_parser
        )
        root = etree.fromstring(MINIMAL_211_DATA_SET)
        self.from_minimal_data = parser.parse_service(
            root.find('Agency/Site/SiteService'),
            self.organization_id_passed_to_parser,
            self.site_id_passed_to_parser
        )

    def test_can_parse_name(self):
        self.assertEqual(self.from_real_data.name, 'Langley Child Development Centre')
        self.assertEqual(self.from_minimal_data.name, 'the service name')

    def test_can_parse_description(self):
        self.assertEqual(self.from_real_data.description[:30], 'Provides inclusive, family-cen')
        self.assertEqual(self.from_minimal_data.description, 'the service description')

    def test_sets_the_organization_id(self):
        self.assertEqual(self.from_real_data.organization_id,
                         self.organization_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.organization_id,
                         self.organization_id_passed_to_parser)

    def test_sets_the_site_id(self):
        self.assertEqual(self.from_real_data.site_id,
                         self.site_id_passed_to_parser)
        self.assertEqual(self.from_minimal_data.site_id,
                         self.site_id_passed_to_parser)

    def test_site_service_description_is_optional(self):
        organization_id = a_string()
        xml_site = '''
        <Site>
            <Key>the site key</Key>
            <Name>the site name</Name>
            <SiteDescription>the site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
            <SiteService>
                <Key>the service key</Key>
                <Name>the service without description</Name>
            </SiteService>
        </Site>
        '''
        root = etree.fromstring(xml_site)
        try:
            parser.parse_site(root, organization_id)
        except MissingRequiredFieldXmlParseException:
            self.fail('MissingRequiredFieldXmlParseException raised unexpectedly')


class AddressParserTests(unittest.TestCase):
    def test_parses_physical_address(self):
        xml_address = '''
            <Site>
                <PhysicalAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>Canada</Country>
                </PhysicalAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'physical_address'
        site_id = a_string()
        address = parser.parse_address(root.find('PhysicalAddress'), site_id, address_type_id)
        self.assertIsInstance(address, dtos.Address)
        self.assertEqual(address.address_type_id, address_type_id)

    def test_parses_postal_address(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>Canada</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        address = parser.parse_address(root.find('MailingAddress'), site_id, address_type_id)
        self.assertIsInstance(address, dtos.Address)
        self.assertEqual(address.address_type_id, address_type_id)

    def test_parses_address_with_only_city_and_country(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <City>City</City>
                    <Country>Canada</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        address = parser.parse_address(root.find('MailingAddress'), site_id, address_type_id)
        self.assertIsInstance(address, dtos.Address)

    def test_replaces_canada_with_corresponding_two_letter_code(self):
        xml_address = '''
            <Site>
                <PhysicalAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>Canada</Country>
                </PhysicalAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address = parser.parse_address(root.find('PhysicalAddress'), a_string(), 'physical_address')
        self.assertEqual(address.country, 'CA')

    def test_replaces_united_states_with_corresponding_two_letter_code(self):
        xml_address = '''
            <Site>
                <PhysicalAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>United States</Country>
                </PhysicalAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address = parser.parse_address(root.find('PhysicalAddress'), a_string(), 'physical_address')
        self.assertEqual(address.country, 'US')

    def test_sets_address_to_none_on_invalid_country(self):
        xml_address = '''
            <Site>
                <PhysicalAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country>All Countries</Country>
                </PhysicalAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address = parser.parse_address(root.find('PhysicalAddress'), a_string(), 'physical_address')
        self.assertIsNone(address)

    def test_sets_city_to_none_when_empty(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City />
                    <Country>Country</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        self.assertIsNone(parser.parse_address(root.find('MailingAddress'), site_id, address_type_id))

    def test_sets_city_to_none_when_missing(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <Country>Country</Country>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        self.assertIsNone(parser.parse_address(root.find('MailingAddress'), site_id, address_type_id))

    def test_sets_country_to_none_when_empty(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                    <Country />
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        self.assertIsNone(parser.parse_address(root.find('MailingAddress'), site_id, address_type_id))

    def test_sets_country_to_none_when_missing(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <City>City</City>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_type_id = 'postal_address'
        site_id = a_string()
        self.assertIsNone(parser.parse_address(root.find('MailingAddress'), site_id, address_type_id))


class AddressLineParserTests(unittest.TestCase):

    def test_parses_lines_1_to_9(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1>Line1</Line1>
                    <Line2>Line2</Line2>
                    <Line3>Line3</Line3>
                    <Line4>Line4</Line4>
                    <Line5>Line5</Line5>
                    <Line6>Line6</Line6>
                    <Line7>Line7</Line7>
                    <Line8>Line8</Line8>
                    <Line9>Line9</Line9>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1\nLine2\nLine3\nLine4\nLine5\nLine6\nLine7\nLine8\nLine9')

    def test_sets_address_to_none_when_empty(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line1 />
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertIsNone(address_lines)

    def test_ignores_invalid_lines(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line0>Line0</Line0>
                    <Line1>Line1</Line1>
                    <Line2 />
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1')

    def test_line_parser_sorts_address_lines(self):
        xml_address = '''
            <Site>
                <MailingAddress>
                    <Line3>Line3</Line3>
                    <Line1>Line1</Line1>
                    <Line2>Line2</Line2>
                </MailingAddress>
            </Site>'''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1\nLine2\nLine3')


class PhoneNumberParserTests(unittest.TestCase):

    def test_does_not_parse_phone_with_empty_phone_type(self):
        site_id = a_string()
        root = etree.fromstring(
            '''
            <Site>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber>123456789</PhoneNumber>
                    <Type />
                </Phone>
            </Site>'''
        )
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(len(phone_numbers), 0)

    def test_does_not_parse_phone_with_empty_phone_number(self):
        site_id = a_string()
        root = etree.fromstring(
            '''
            <Site>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber />
                    <Type>Phone1</Type>
                </Phone>
            </Site>'''
        )
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(len(phone_numbers), 0)

    def test_parses_phone_into_expected_dto_object(self):
        site_id = a_string()
        phone_type = a_string()
        phone_number = a_phone_number()
        xml = self.build_phone_xml(phone_number, phone_type)
        root = etree.fromstring(xml)
        phone_number_list = parser.parse_site_phone_number_list(root, site_id)
        self.assertIsInstance(phone_number_list[0], dtos.PhoneAtLocation)

    def test_parses_phone_type_and_converts_to_id(self):
        site_id = a_string()
        phone_type = 'A phone TYPE'
        phone_number = a_phone_number()
        xml = self.build_phone_xml(phone_number, phone_type)
        root = etree.fromstring(xml)
        phone_number_list = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_number_list[0].phone_number_type_id, 'a_phone_type')

    def test_parses_phone_phone_number(self):
        site_id = a_string()
        phone_type = a_string()
        phone_number = a_phone_number()
        xml = self.build_phone_xml(phone_number, phone_type)
        root = etree.fromstring(xml)
        phone_number_list = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_number_list[0].phone_number, phone_number)

    def test_parses_only_phone_numbers(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-888-425-2666', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-888-425-2666')

    def test_parses_phone_with_full_mnemonics(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-888-4AL-ANON (1-888-425-2666)', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-888-425-2666')
    
    def test_not_parse_phone_with_partial_mnemonics(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-800-222-TIPS (8477)', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-800-222-8477')

    def test_parse_phone_with_extension(self):
        site_id = a_string()
        xml = self.build_phone_xml('250-542-3555 Local 221', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-542-3555')

    def test_parse_phone_with_area_code(self):
        site_id = a_string()
        xml = self.build_phone_xml('(250)-541-2200', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-541-2200')
    
    def test_parse_phone_with_area_code_and_extension(self):
        site_id = a_string()
        xml = self.build_phone_xml('(250)-541-2200 Ext 221', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-541-2200')
    
    def test_parse_phone_with_mnemonics_and_number_mixed_in(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-844-START11 (782-7811)', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-844-782-7811')

    def test_parse_phone_with_longer_mnemonics(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-855-55-MERCY (63729)', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-855-556-3729')
    
    def test_parse_phone_with_more_than_one_number(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-866-235-0350; 613-731-4092', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-866-235-0350')

    def test_parse_phone_with_only_mnemonics(self):
        site_id = a_string()
        xml = self.build_phone_xml('1-888-tai-chi-1', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-888-824-2441')
    
    def test_parse_phone_with_short_numbers(self):
        site_id = a_string()
        xml = self.build_phone_xml('211NS (21167)', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '21167')

    def test_parse_phone_with_missing_hyphen(self):
        site_id = a_string()
        xml = self.build_phone_xml('250 832-3885 Local 1310', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-832-3885')

    def test_parse_phone_with_no_hyphen(self):
        site_id = a_string()
        xml = self.build_phone_xml('12508323885', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-250-832-3885')

    def test_parse_phone_with_area_code_extension_no_hyphen(self):
        site_id = a_string()
        xml = self.build_phone_xml('1(250)8323885 local 101', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-250-832-3885')

    def test_parse_two_numbers_separated_by_or(self):
        site_id = a_string()
        xml = self.build_phone_xml('250-286-9766 or 1-866-286-9766', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-866-286-9766')
    
    def test_parse_two_numbers_separated_by_slash(self):
        site_id = a_string()
        xml = self.build_phone_xml('250-949-6625 / 250-286-8064', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-286-8064')

    def test_parse_mnemonics_and_extension(self):
        site_id = a_string()
        xml = self.build_phone_xml('250-949-HELP (4357) local 101', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-949-4357')

    def test_parse_area_code_and_extension(self):
        site_id = a_string()
        xml = self.build_phone_xml('(250)-949-HELP (4357) local 101', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '250-949-4357')
    
    def test_parse_two_mnemonic_phone_numbers(self):
        site_id = a_string()
        xml = self.build_phone_xml('(250)-949-HELP (4357) local 101 or 1-844-START11 (782-7811) ext 102', a_string())
        root = etree.fromstring(xml)
        phone_numbers = parser.parse_site_phone_number_list(root, site_id)
        self.assertEqual(phone_numbers[0].phone_number, '1-844-782-7811')

    def build_phone_xml(self, phone_number, phone_number_type):
        return '''
            <Site>
                <Phone TollFree="false" Confidential="false">
                    <PhoneNumber>{}</PhoneNumber>
                    <Type>{}</Type>
                </Phone>
            </Site>'''.format(phone_number, phone_number_type)


class HTMLMarkupParserTests(unittest.TestCase):
    def test_removes_doubly_escaped_bold_markup_from_required_field(self):
        xml_agency_key = '''
        <Source>
            <Agency>
                <Key>&amp;lt;b&amp;gt;abc</Key>
            </Agency>
        </Source>
        '''
        root = etree.fromstring(xml_agency_key)
        html_markup = parser.parse_agency_key(root.find('Agency'))
        self.assertEqual(html_markup, 'abc')

    def test_removes_doubly_escaped_strong_markup_from_required_field(self):
        xml_agency_key = '''
        <Source>
            <Agency>
                <Key>&amp;lt;strong&amp;gt;abc</Key>
            </Agency>
        </Source>
        '''
        root = etree.fromstring(xml_agency_key)
        html_markup = parser.parse_agency_key(root.find('Agency'))
        self.assertEqual(html_markup, 'abc')

    def test_removes_doubly_escaped_bold_markup_from_optional_field(self):
        xml_address = '''
        <Site>
            <MailingAddress>
                <Line1>&amp;lt;b&amp;gt;Line1</Line1>
            </MailingAddress>
        </Site>
        '''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1')

    def test_removes_doubly_escaped_strong_markup_from_optional_field(self):
        xml_address = '''
        <Site>
            <MailingAddress>
                <Line1>&amp;lt;strong&amp;gt;Line1</Line1>
            </MailingAddress>
        </Site>
        '''
        root = etree.fromstring(xml_address)
        address_lines = parser.parse_address_lines(root.find('MailingAddress'))
        self.assertEqual(address_lines, 'Line1')
