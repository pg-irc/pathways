import string
from datetime import date
from django.test import TestCase
from bc211.open_referral_csv_import.inactive_records_collector import InactiveRecordsCollector
from bc211.import_counters import ImportCounters
from bc211.open_referral_csv_import.organization import import_organization
from bc211.open_referral_csv_import.service import import_service
from bc211.open_referral_csv_import.location import import_location
from bc211.open_referral_csv_import.service_at_location import import_service_at_location
from bc211.open_referral_csv_import.address import import_address, import_location_address
from bc211.open_referral_csv_import.phone import import_phone
from bc211.open_referral_csv_import.taxonomy import import_taxonomy
from bc211.open_referral_csv_import.service_taxonomy import(read_and_import_rows)
from bc211.open_referral_csv_import.tests.helpers import (
    OpenReferralCsvOrganizationBuilder, OpenReferralCsvServiceBuilder,
    OpenReferralCsvLocationBuilder, OpenReferralCsvServiceAtLocationBuilder,
    OpenReferralCsvAddressBuilder, OpenReferralCsvPhoneBuilder, OpenReferralCsvTaxonomyBuilder,
    OpenReferralCsvServiceTaxonomyBuilder)
from common.testhelpers.random_test_values import (a_string, an_email_address, a_website_address,
                                 a_latitude, a_longitude, a_phone_number, a_country_code)
from human_services.organizations.models import Organization
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from human_services.locations.tests.helpers import LocationBuilder
from human_services.services.models import Service
from human_services.locations.models import Location, ServiceAtLocation
from human_services.addresses.models import Address, AddressType
from human_services.locations.models import LocationAddress
from human_services.phone_at_location.models import PhoneNumberType, PhoneAtLocation
from taxonomies.tests.helpers import TaxonomyTermBuilder
from taxonomies.models import TaxonomyTerm



class OrganizationImporterTests(TestCase):
    def test_can_import_id(self):
        the_id = a_string()
        organization_data = OpenReferralCsvOrganizationBuilder().with_id(the_id).build()
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].id, the_id)

    def test_can_import_name(self):
        the_name = a_string()
        organization_data = OpenReferralCsvOrganizationBuilder().with_name(the_name).build()
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].name, the_name)

    def test_can_import_alternate_name(self):
        the_alternate_name = a_string()
        organization_data = (OpenReferralCsvOrganizationBuilder().
                             with_alternate_name(the_alternate_name).
                             build())
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].alternate_name, the_alternate_name)

    def test_can_import_description(self):
        the_description = a_string()
        organization_data = (OpenReferralCsvOrganizationBuilder().
                             with_description(the_description).
                             build())
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].description, the_description)

    def test_can_import_email(self):
        the_email = an_email_address()
        organization_data = OpenReferralCsvOrganizationBuilder().with_email(the_email).build()
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].email, the_email)

    def test_can_import_website(self):
        the_website = a_website_address()
        organization_data = OpenReferralCsvOrganizationBuilder().with_url(the_website).build()
        import_organization(organization_data, InactiveRecordsCollector(), ImportCounters())
        organizations = Organization.objects.all()
        self.assertEqual(organizations[0].website, the_website)


class ServiceImporterTests(TestCase):
    def setUp(self):
        self.organization_id = a_string()
        self.organization = OrganizationBuilder().with_id(self.organization_id).create()

    def test_can_import_id(self):
        the_id = a_string()
        service_data = OpenReferralCsvServiceBuilder(self.organization).with_id(the_id).build()
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].id, the_id)

    def test_can_import_organization_id(self):
        service_data = OpenReferralCsvServiceBuilder(self.organization).build()
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].organization_id, self.organization_id)

    def test_can_import_name(self):
        the_name = a_string()
        service_data = OpenReferralCsvServiceBuilder(self.organization).with_name(the_name).build()
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].name, the_name)

    def test_can_import_alternate_name(self):
        the_alternate_name = a_string()
        service_data = (OpenReferralCsvServiceBuilder(self.organization).
                        with_alternate_name(the_alternate_name).
                        build())
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].alternate_name, the_alternate_name)

    def test_can_import_description(self):
        the_description = a_string()
        service_data = (OpenReferralCsvServiceBuilder(self.organization).
                        with_description(the_description).
                        build())
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].description, the_description)

    def test_can_import_website(self):
        the_website = a_website_address()
        service_data = (OpenReferralCsvServiceBuilder(self.organization).
                        with_url(the_website).
                        build())
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].website, the_website)

    def test_can_import_email(self):
        the_email = an_email_address()
        service_data = (OpenReferralCsvServiceBuilder(self.organization).
                        with_email(the_email).
                        build())
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(services[0].email, the_email)

    def test_can_import_last_verified_date(self):
        the_date = '2020-01-25'
        service_data = (OpenReferralCsvServiceBuilder(self.organization).
                        with_last_verified_on(the_date).
                        build())
        import_service(service_data, InactiveRecordsCollector(), ImportCounters())
        services = Service.objects.all()
        self.assertEqual(date.strftime(services[0].last_verified_date, "%Y-%m-%d"), the_date)


class LocationImporterTests(TestCase):
    def setUp(self):
        self.organization_id = a_string()
        self.organization = OrganizationBuilder().with_id(self.organization_id).create()

    def test_can_import_id(self):
        the_id = a_string()
        location_data = OpenReferralCsvLocationBuilder(self.organization).with_id(the_id).build()
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].id, the_id)

    def test_can_import_organization_id(self):
        location_data = OpenReferralCsvLocationBuilder(self.organization).build()
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].organization_id, self.organization_id)

    def test_can_import_name(self):
        the_name = a_string()
        location_data = (OpenReferralCsvLocationBuilder(self.organization).
                        with_name(the_name).
                        build())
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].name, the_name)

    def test_can_import_alternate_name(self):
        the_alternate_name = a_string()
        location_data = (OpenReferralCsvLocationBuilder(self.organization).
                        with_alternate_name(the_alternate_name).
                        build())
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].alternate_name, the_alternate_name)

    def test_can_import_description(self):
        the_description = a_string()
        location_data = (OpenReferralCsvLocationBuilder(self.organization).
                        with_description(the_description).
                        build())
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].description, the_description)

    def test_can_import_point(self):
        the_latitude = a_latitude()
        the_longitude = a_longitude()
        location_data = (OpenReferralCsvLocationBuilder(self.organization).
                        with_latitude(str(the_latitude)).
                        with_longitude(str(the_longitude)).
                        build())
        import_location(location_data, InactiveRecordsCollector(), ImportCounters())
        locations = Location.objects.all()
        self.assertEqual(locations[0].point.x, the_longitude)
        self.assertEqual(locations[0].point.y, the_latitude)


class ServiceAtLocationImporterTests(TestCase):
    def setUp(self):
        organization = OrganizationBuilder().create()
        self.service_id = a_string()
        self.location_id = a_string()
        self.service = ServiceBuilder(organization).with_id(self.service_id).create()
        self.location = LocationBuilder(organization).with_id(self.location_id).create()

    def test_can_import_service_id(self):
        service_data = OpenReferralCsvServiceAtLocationBuilder(self.service, self.location).build()
        import_service_at_location(service_data, ImportCounters())
        services_at_location = ServiceAtLocation.objects.all()
        self.assertEqual(services_at_location[0].service_id, self.service_id)

    def test_can_import_location_id(self):
        service_data = OpenReferralCsvServiceAtLocationBuilder(self.service, self.location).build()
        import_service_at_location(service_data, ImportCounters())
        services_at_location = ServiceAtLocation.objects.all()
        self.assertEqual(services_at_location[0].location_id, self.location_id)


class AddressImporterTests(TestCase):
    def setUp(self):
        organization = OrganizationBuilder().create()
        self.location_id = a_string()
        self.location = LocationBuilder(organization).with_id(self.location_id).create()

    def test_can_import_id(self):
        the_id = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_address_id(the_id).build()
        import_address(address_data, ImportCounters()
        )
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].id, the_id)

    def test_can_import_city(self):
        the_city = a_string()
        address_data = OpenReferralCsvAddressBuilder(self.location).with_city(the_city).build()
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].city, the_city)

    def test_can_import_country(self):
        the_country = a_country_code()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                        with_country(the_country).
                        build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].country, the_country)

    def test_can_import_attention(self):
        the_attention = a_string()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                        with_attention(the_attention).
                        build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].attention, the_attention)

    def test_can_import_address(self):
        the_address_1 = a_string()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                        with_address_1(the_address_1).
                        build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].address, the_address_1)

    def test_can_import_addresses(self):
        the_address_1 = a_string()
        the_address_2 = a_string()
        the_address_3 = a_string()
        the_address_4 = a_string()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                        with_address_1(the_address_1).
                        with_address_2(the_address_2).
                        with_address_3(the_address_3).
                        with_address_4(the_address_4).
                        build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(
            addresses[0].address, 
            f'{the_address_1}\n{the_address_2}\n{the_address_3}\n{the_address_4}'
        )

    def test_can_import_state_province(self):
        the_state_province = a_string()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                        with_state_province(the_state_province).
                        build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].state_province, the_state_province)

    def test_can_import_postal_code(self):
        the_postal_code = a_string()
        address_data = (OpenReferralCsvAddressBuilder(self.location).
                            with_postal_code(the_postal_code).
                            build())
        import_address(address_data, ImportCounters())
        addresses = Address.objects.all()
        self.assertEqual(addresses[0].postal_code, the_postal_code)


class LocationAddressImporterTests(TestCase):
    def setUp(self):
        organization = OrganizationBuilder().create()
        self.location_id = a_string()
        self.location = LocationBuilder(organization).with_id(self.location_id).create()
        self.address_id = a_string()
        self.address_type = 'postal_address'
        self.address_data = (OpenReferralCsvAddressBuilder(self.location).
                                with_address_id(self.address_id).
                                with_address_type(self.address_type).
                                build())
        import_address(self.address_data, ImportCounters())
        self.address = Address.objects.get(pk=self.address_id)

    def test_can_import_address_id(self):
        import_location_address(
            self.address_data,
            self.address,
            InactiveRecordsCollector(),
            ImportCounters())
        location_addresses = LocationAddress.objects.all()
        self.assertEqual(location_addresses[0].address_id, self.address_id)

    def test_can_import_location_id(self):
        import_location_address(
            self.address_data,
            self.address,
            InactiveRecordsCollector(),
            ImportCounters())
        location_addresses = LocationAddress.objects.all()
        self.assertEqual(location_addresses[0].location_id, self.location_id)

    def test_can_import_address_type(self):
        import_location_address(
            self.address_data,
            self.address,
            InactiveRecordsCollector(),
            ImportCounters())
        location_addresses = LocationAddress.objects.all()
        the_address_type_instance = AddressType.objects.get(pk=self.address_type)
        self.assertEqual(location_addresses[0].address_type, the_address_type_instance)


class PhoneAtLocationImporterTests(TestCase):
    def setUp(self):
        organization = OrganizationBuilder().create()
        self.location_id = a_string()
        self.location = LocationBuilder(organization).with_id(self.location_id).create()

    def test_can_import_location_id(self):
        phone_data = OpenReferralCsvPhoneBuilder(self.location).build()
        import_phone(phone_data, InactiveRecordsCollector(), ImportCounters())
        phones_at_location = PhoneAtLocation.objects.all()
        self.assertEqual(phones_at_location[0].location_id, self.location_id)

    def test_can_import_phone_number_type(self):
        the_phone_type = a_string()
        phone_data = (OpenReferralCsvPhoneBuilder(self.location).
                        with_phone_type(the_phone_type).
                        build())
        import_phone(phone_data, InactiveRecordsCollector(), ImportCounters())
        phones_at_location = PhoneAtLocation.objects.all()
        the_phone_number_type_instance = PhoneNumberType.objects.get(pk=the_phone_type)
        self.assertEqual(phones_at_location[0].phone_number_type, the_phone_number_type_instance)

    def test_can_import_phone_number(self):
        the_phone_number = a_phone_number()
        phone_data = (OpenReferralCsvPhoneBuilder(self.location).
                        with_number(the_phone_number).
                        build())
        import_phone(phone_data, InactiveRecordsCollector(), ImportCounters())
        phones_at_location = PhoneAtLocation.objects.all()
        self.assertEqual(phones_at_location[0].phone_number, the_phone_number)


class TaxonomyImporterTests(TestCase):
    def test_can_import_taxonomy_id(self):
        the_taxonomy_id = a_string()
        taxonomy_data = OpenReferralCsvTaxonomyBuilder().with_taxonomy_id(the_taxonomy_id).build()
        import_taxonomy(taxonomy_data, ImportCounters())
        taxonomy_terms = TaxonomyTerm.objects.all()
        self.assertEqual(taxonomy_terms[0].taxonomy_id, the_taxonomy_id)

    def test_can_import_name(self):
        the_name = a_string()
        taxonomy_data = OpenReferralCsvTaxonomyBuilder().with_name(the_name).build()
        import_taxonomy(taxonomy_data, ImportCounters())
        taxonomy_terms = TaxonomyTerm.objects.all()
        self.assertEqual(taxonomy_terms[0].name, the_name)


class ServiceTaxonomyImporterTests(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().create()
        self.taxonomy_id = a_string()
        self.taxonomy_term = TaxonomyTermBuilder().with_taxonomy_id(self.taxonomy_id).create()
        self.service_id = a_string()
        ServiceBuilder(self.organization).with_id(self.service_id).create()

    def test_can_import_one_taxonomy_term_into_service_record(self):
        service_taxonomy_data = (OpenReferralCsvServiceTaxonomyBuilder().
                                 with_service_id(self.service_id).
                                 with_taxonomy_id(self.taxonomy_id).
                                 build())
        csv_data = [service_taxonomy_data]
        read_and_import_rows(csv_data, InactiveRecordsCollector())
        service = Service.objects.get(pk=self.service_id)
        service_taxonomy_terms = service.taxonomy_terms.all()
        self.assertEqual(service_taxonomy_terms[0], self.taxonomy_term)

    def test_can_import_multiple_taxonomy_terms_into_the_same_service_record(self):
        second_taxonomy_id = a_string()
        second_taxonomy_term = TaxonomyTermBuilder().with_taxonomy_id(second_taxonomy_id).create()
        first_service_taxonomy_data = (OpenReferralCsvServiceTaxonomyBuilder().
                                       with_service_id(self.service_id).
                                       with_taxonomy_id(self.taxonomy_id).
                                       build())
        second_service_taxonomy_data = (OpenReferralCsvServiceTaxonomyBuilder().
                                        with_service_id(self.service_id).
                                        with_taxonomy_id(second_taxonomy_id).
                                        build())
        csv_data = [first_service_taxonomy_data, second_service_taxonomy_data]
        read_and_import_rows(csv_data, InactiveRecordsCollector())
        service_active_record = Service.objects.get(pk=self.service_id)
        service_taxonomy_terms = service_active_record.taxonomy_terms.all()
        self.assertEqual(service_taxonomy_terms[0], self.taxonomy_term)
        self.assertEqual(service_taxonomy_terms[1], second_taxonomy_term)

    def test_does_not_import_a_second_taxonomy_term_when_the_service_id_is_different(self):
        second_service_id = a_string()
        ServiceBuilder(self.organization).with_id(second_service_id).create()
        second_taxonomy_id = a_string()
        TaxonomyTermBuilder().with_taxonomy_id(second_taxonomy_id).create()
        first_service_taxonomy_data = (OpenReferralCsvServiceTaxonomyBuilder().
                                       with_service_id(self.service_id).
                                       with_taxonomy_id(self.taxonomy_id).
                                       build())
        second_service_taxonomy_data = (OpenReferralCsvServiceTaxonomyBuilder().
                                        with_service_id(second_service_id).
                                        with_taxonomy_id(second_taxonomy_id).
                                        build())
        csv_data = [first_service_taxonomy_data, second_service_taxonomy_data]
        read_and_import_rows(csv_data, InactiveRecordsCollector())
        first_service = Service.objects.get(pk=self.service_id)
        first_service_taxonomy_terms = first_service.taxonomy_terms.all()
        self.assertEqual(len(first_service_taxonomy_terms), 1)
        self.assertEqual(first_service_taxonomy_terms[0], self.taxonomy_term)
