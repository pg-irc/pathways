import logging
from bc211.importer import save_records_to_database, save_locations, save_services
from bc211.parser import read_records_from_file
from bc211.import_counters import ImportCounters
from common.testhelpers.random_test_values import a_string
from django.test import TestCase
from human_services.locations.models import Location
from human_services.locations.tests.helpers import LocationBuilder
from human_services.organizations.models import Organization
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.models import Service
from human_services.services.tests.helpers import ServiceBuilder
from human_services.addresses.models import Address, AddressType
from taxonomies.models import TaxonomyTerm

logging.disable(logging.ERROR)

ONE_AGENCY_FIXTURE = 'bc211/data/BC211_data_one_agency.xml'
MULTI_AGENCY_FIXTURE = 'bc211/data/BC211_data_excerpt.xml'
SHARED_SERVICE_FIXTURE = 'bc211/data/BC211_data_service_53489235_at_two_sites.xml'
INVALID_AGENCIES_FIXTURE = 'bc211/data/BC211_data_with_invalid_agencies.xml'


class LocationImportTests(TestCase):
    def setUp(self):
        file = open(ONE_AGENCY_FIXTURE, 'r')
        records = read_records_from_file(file)
        save_records_to_database(records, ImportCounters())
        all_records_from_database = Location.objects.all()
        self.location = all_records_from_database[0]

    def test_can_import_name(self):
        self.assertEqual(self.location.name, 'Langley Child Development Centre')

    def test_can_import_description(self):
        self.assertEqual(self.location.description[:30], 'Provides inclusive, family-cen')

    def test_can_import_latitude(self):
        self.assertAlmostEqual(self.location.point.y, 49.087284)

    def test_can_import_longitude(self):
        self.assertAlmostEqual(self.location.point.x, -122.607918)


class InactiveDataImportTests(TestCase):

    def test_do_not_import_inactive_organization(self):
        inactive_description = 'DEL ' + a_string()
        inactive_organization = OrganizationBuilder().with_description(inactive_description).build_dto()
        active_organization = OrganizationBuilder().build_dto()

        organizations = iter([inactive_organization, active_organization])
        save_records_to_database(organizations, ImportCounters())
        all_records_from_database = Organization.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_organization.id)

    def test_do_not_import_inactive_location(self):
        organization = OrganizationBuilder().create()
        inactive_description = 'DEL ' + a_string()
        inactive_location = LocationBuilder(organization).with_description(inactive_description).build_dto()
        active_location = LocationBuilder(organization).build_dto()

        save_locations([inactive_location, active_location], ImportCounters())
        all_records_from_database = Location.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_location.id)

    def test_do_not_import_inactive_service(self):
        organization = OrganizationBuilder().create()
        location = LocationBuilder(organization).create()
        inactive_description = 'DEL ' + a_string()
        inactive_service = (ServiceBuilder(organization).
                            with_location(location).
                            with_description(inactive_description).
                            build_dto())
        active_service = (ServiceBuilder(organization).
                          with_location(location).
                          build_dto())

        save_services([inactive_service, active_service], ImportCounters())
        all_records_from_database = Service.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_service.id)


class OrganizationImportTests(TestCase):
    def setUp(self):
        save_records_to_database(read_records_from_file(open(ONE_AGENCY_FIXTURE, 'r')), ImportCounters())
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


class InvalidOrganizationImportTests(TestCase):
    def test_save_organizations_catches_exceptions(self):
        save_records_to_database(read_records_from_file(open(INVALID_AGENCIES_FIXTURE, 'r')), ImportCounters())
        organizations = Organization.objects.all()
        organization_ids = list(map(lambda x: x.id, organizations))

        self.assertEqual(len(organization_ids), 2)
        self.assertIn('SECOND_VALID_AGENCY', organization_ids)
        self.assertIn('FIRST_VALID_AGENCY', organization_ids)


class ServiceImportTests(TestCase):
    def setUp(self):
        file = open(MULTI_AGENCY_FIXTURE, 'r')
        save_records_to_database(read_records_from_file(file), ImportCounters())
        self.all_taxonomy_terms = TaxonomyTerm.objects.all()
        self.all_services = Service.objects.all()

    def test_service_has_correct_taxonomy_terms(self):
        last_post_fund_service_id = 9487370
        expected_last_post_fund_service_taxonony_terms = [
            self.all_taxonomy_terms.get(taxonomy_id='bc211-what', name='financial-assistance'),
            self.all_taxonomy_terms.get(taxonomy_id='bc211-why', name='funerals'),
            self.all_taxonomy_terms.get(taxonomy_id='bc211-who', name='veterans'),
        ]

        last_post_fund_service = self.all_services.get(id=last_post_fund_service_id)
        last_post_fund_service_taxonomy_terms = last_post_fund_service.taxonomy_terms.all()

        self.assertCountEqual(last_post_fund_service_taxonomy_terms,
                              expected_last_post_fund_service_taxonony_terms)

    def testTwoServicesCanBeRelatedToOneLocation(self):
        file = open(SHARED_SERVICE_FIXTURE, 'r')
        save_records_to_database(read_records_from_file(file), ImportCounters())
        self.assertEqual(Service.objects.filter(locations__id='9493390').count(), 2)


class AddressImportTests(TestCase):
    def setUp(self):
        file = open(ONE_AGENCY_FIXTURE, 'r')
        records = read_records_from_file(file)
        save_records_to_database(records, ImportCounters())
        self.addresses = Address.objects.all()

    def test_can_import_address(self):
        self.assertIsInstance(self.addresses.first(), Address)

    def test_does_not_import_duplicates(self):
        self.assertEqual(len(self.addresses), 1)


class AddressTypeTests(TestCase):
    def test_imports_correct_address_types(self):
        expected_address_types = [
            AddressType(id='physical_address'),
            AddressType(id='postal_address')
        ]
        self.assertCountEqual(AddressType.objects.all(), expected_address_types)


class FullDataImportTests(TestCase):
    def setUp(self):
        file = open(MULTI_AGENCY_FIXTURE, 'r')
        self.counts = ImportCounters()
        save_records_to_database(read_records_from_file(file), self.counts)
        self.all_locations = Location.objects.all()
        self.all_organizations = Organization.objects.all()
        self.all_taxonomy_terms = TaxonomyTerm.objects.all()

    # breaking one-assert-per-test rule to speed up running tests by only calling setup once for all the below checks
    def test_can_import_full_data_set(self):
        self.assertEqual(len(self.all_organizations), 16)
        self.assertEqual(len(self.all_locations), 40)
        self.assertEqual(len(self.all_taxonomy_terms), 134)
        self.assertEqual(self.counts.organization_count, 16)
        self.assertEqual(self.counts.location_count, 40)
        self.assertEqual(self.counts.taxonomy_term_count, 134)
        self.assertEqual(self.counts.address_count, 36)
        self.assertEqual(self.counts.phone_number_types_count, 5)
        self.assertEqual(self.counts.phone_at_location_count, 86)
