import logging
from bc211.import_icarol_xml.importer import handle_parser_errors, update_entire_organization
from bc211.service import update_services_for_location
from bc211.import_icarol_xml.location import update_locations
from bc211.import_icarol_xml.import_counters import ImportCounters
from common.testhelpers.random_test_values import a_string
from django.contrib.gis.geos import Point
from django.test import TestCase
from human_services.locations.models import Location
from human_services.locations.tests.helpers import LocationBuilder
from human_services.organizations.models import Organization
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.models import Service
from human_services.services.tests.helpers import ServiceBuilder
from human_services.addresses.models import Address, AddressType
from human_services.addresses.tests.helpers import AddressBuilder
from taxonomies.models import TaxonomyTerm
import xml.etree.ElementTree as etree
from bc211.import_icarol_xml.parser import parse_agency


logging.disable(logging.ERROR)

ONE_AGENCY_FIXTURE = 'bc211/import_icarol_xml/tests/data/BC211_data_one_agency.xml'
MULTI_AGENCY_FIXTURE = 'bc211/import_icarol_xml/tests/data/BC211_data_excerpt.xml'
SHARED_SERVICE_FIXTURE = 'bc211/import_icarol_xml/tests/data/BC211_data_service_53489235_at_two_sites.xml'
INVALID_AGENCIES_FIXTURE = 'bc211/import_icarol_xml/tests/data/BC211_data_with_invalid_agencies.xml'


def read_records_from_file(file):
    xml = file.read()
    return parse(xml)


def parse(xml_data_as_string):
    root_xml = etree.fromstring(xml_data_as_string)
    agencies = root_xml.findall('Agency')
    return map(parse_agency, agencies)


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


def save_records_to_database(organizations, counters):
    for organization in handle_parser_errors(organizations):
        update_entire_organization(organization, {}, counters)


class LocationWithMissingLatLongImportTests(TestCase):
    def setUp(self):
        file = open(ONE_AGENCY_FIXTURE, 'r')
        records = read_records_from_file(file)
        save_records_to_database(records, ImportCounters())
        all_records_from_database = Location.objects.all()
        self.location = all_records_from_database[0]

    def test_can_replace_missing_lat_long_with_city_lat_long(self):
        organization = OrganizationBuilder().create()
        location_id = a_string()
        address_in_vancouver = (AddressBuilder().
                                with_city('Vancouver').
                                with_address_type('physical_address').
                                with_location_id(location_id).
                                build_dto())
        location_without_latlong = (LocationBuilder(organization).
                                    with_id(location_id).
                                    with_point(None).
                                    with_physical_address(address_in_vancouver).
                                    build_dto())

        update_locations([location_without_latlong], organization.id, {'Vancouver': Point(-123.120738, 49.282729)}, ImportCounters())

        self.assertAlmostEqual(location_without_latlong.spatial_location.latitude, 49.282729)
        self.assertAlmostEqual(location_without_latlong.spatial_location.longitude, -123.120738)

    def test_no_lat_long_or_city_lat_long(self):
        organization = OrganizationBuilder().create()
        location_id = a_string()
        address_in_vancouver = (AddressBuilder().
                                with_city('Vancouver').
                                with_address_type('physical_address').
                                with_location_id(location_id).
                                build_dto())
        location_without_latlong = (LocationBuilder(organization).
                                    with_id(location_id).
                                    with_point(None).
                                    with_physical_address(address_in_vancouver).
                                    build_dto())

        update_locations([location_without_latlong], organization.id, {}, ImportCounters())

        self.assertEqual(location_without_latlong.spatial_location, None)


class InactiveDataImportTests(TestCase):

    def test_do_not_import_inactive_organization_prefixed_with_DEL_and_number(self):
        inactive_description = 'DEL14 ' + a_string()
        inactive_organization = OrganizationBuilder().with_description(inactive_description).build_dto()
        active_organization = OrganizationBuilder().build_dto()

        organizations = iter([inactive_organization, active_organization])
        save_records_to_database(organizations, ImportCounters())
        all_records_from_database = Organization.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_organization.id)

    def test_do_not_import_inactive_organization_prefixed_with_tab_DEL_and_number(self):
        inactive_description = '\tDEL15 ' + a_string()
        inactive_organization = OrganizationBuilder().with_description(inactive_description).build_dto()
        active_organization = OrganizationBuilder().build_dto()

        organizations = iter([inactive_organization, active_organization])
        save_records_to_database(organizations, ImportCounters())
        all_records_from_database = Organization.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_organization.id)

    def test_do_not_import_inactive_location_and_number(self):
        organization = OrganizationBuilder().create()
        inactive_description = 'DEL16 ' + a_string()
        inactive_location = LocationBuilder(organization).with_description(inactive_description).build_dto()
        active_location = LocationBuilder(organization).build_dto()

        update_locations([inactive_location, active_location], organization.id, {}, ImportCounters())
        all_records_from_database = Location.objects.all()

        self.assertEqual(len(all_records_from_database), 1)
        self.assertEqual(all_records_from_database[0].id, active_location.id)

    def test_do_not_import_inactive_service(self):
        organization = OrganizationBuilder().create()
        location = LocationBuilder(organization).create()
        inactive_description = 'DEL17 ' + a_string()
        inactive_service = (ServiceBuilder(organization).
                            with_location(location).
                            with_description(inactive_description).
                            build_dto())
        active_service = (ServiceBuilder(organization).
                          with_location(location).
                          build_dto())

        update_services_for_location(location.id, [inactive_service, active_service], ImportCounters())
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

    def test_two_services_can_be_related_to_one_location(self):
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
        self.assertEqual(len(self.all_organizations), 15)
        self.assertEqual(len(self.all_locations), 39)
        self.assertEqual(len(self.all_taxonomy_terms), 129)
        self.assertEqual(self.counts.organizations_created, 15)
        self.assertEqual(self.counts.locations_created, 39)
        self.assertEqual(self.counts.taxonomy_term_count, 129)
        self.assertEqual(self.counts.address_count, 35)
        self.assertEqual(self.counts.phone_number_types_count, 5)
        self.assertEqual(self.counts.phone_at_location_count, 84)
