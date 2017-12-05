import unittest
import logging
import xml.etree.ElementTree as etree
from bc211 import parser

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
        </Site>
        <Site>
            <Key>the second site key</Key>
            <Name>the second site name</Name>
            <SiteDescription>the second site description</SiteDescription>
            <SpatialLocation>
                <Latitude>123.456</Latitude>
                <Longitude>-154.321</Longitude>
            </SpatialLocation>
        </Site>
    </Agency>
</Source>'''

class BC211ParserTests(unittest.TestCase):
    def test_parse_many_locations(self):
        file_open_for_reading = open(MULTI_AGENCY__211_DATA_SET, 'r')
        xml = file_open_for_reading.read()
        organizations = list(parser.parse(xml))
        locations_from_first_organization = list(organizations[0].locations)
        self.assertEqual(len(organizations), 16)
        self.assertEqual(len(locations_from_first_organization), 1)


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
