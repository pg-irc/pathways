import logging
from django.test import TestCase
from bc211.parser import read_records_from_file
from bc211.importer import save_records_to_database
from organizations.models import Organization
from locations.models import Location

logging.disable(logging.ERROR)

ONE_AGENCY_FIXTURE = 'bc211/data/BC211_data_one_agency.xml'
MULTI_AGENCY_FIXTURE = 'bc211/data/BC211_data_excerpt.xml'

class LocationImportTests(TestCase):
    def setUp(self):
        file = open(ONE_AGENCY_FIXTURE, 'r')
        records = read_records_from_file(file)
        save_records_to_database(records)
        all_records_from_database = Location.objects.all()
        self.location = all_records_from_database[0]

    def test_can_import_name(self):
        self.assertEqual(self.location.name, 'Langley Child Development Centre')

    def test_can_import_description(self):
        self.assertEqual(self.location.description[:30], 'Provides inclusive, family-cen')

    def test_can_import_latitude(self):
        self.assertAlmostEqual(self.location.latitude, 49.087284)

    def test_can_import_longitude(self):
        self.assertAlmostEqual(self.location.longitude, -122.607918)


class OrganizationImportTests(TestCase):
    def setUp(self):
        save_records_to_database(read_records_from_file(open(ONE_AGENCY_FIXTURE, 'r')))
        organizations = Organization.objects.all()
        self.organization = organizations[0]

    def test_can_import_id(self):
        self.assertEqual(self.organization.id, '9487364')

    def test_can_import_name(self):
        self.assertEqual(self.organization.name, 'Langley Child Development Centre')

    def test_can_import_description(self):
        self.assertEqual(self.organization.description[:30], 'Provides inclusive, family-cen')

    def test_can_import_website(self):
        self.assertEqual(self.organization.website, 'http://www.langleycdc.com')

    def test_can_import_email(self):
        self.assertEqual(self.organization.email, 'info@langleycdc.com')


class FullDataImportTests(TestCase):
    def setUp(self):
        file = open(MULTI_AGENCY_FIXTURE, 'r')
        self.return_value = save_records_to_database(read_records_from_file(file))
        self.all_locations = Location.objects.all()
        self.all_organizations = Organization.objects.all()

    def test_can_import_multiple_organizations(self):
        self.assertEqual(len(self.all_organizations), 16)

    def test_can_import_multiple_locations(self):
        self.assertEqual(len(self.all_locations), 40)

    def test_returns_number_of_organizations_imported(self):
        self.assertEqual(self.return_value.organization_count, 16)

    def test_returns_number_of_locations_imported(self):
        self.assertEqual(self.return_value.location_count, 40)
