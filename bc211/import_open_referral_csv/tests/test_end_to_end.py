from django.test import TestCase
from bc211.import_open_referral_csv.inactive_records_collector import InactiveRecordsCollector
from bc211.import_icarol_xml.import_counters import ImportCounters
from bc211.import_open_referral_csv.organization import read_and_import_rows as import_organization
from bc211.import_open_referral_csv.location import read_and_import_row as import_locations
from bc211.import_open_referral_csv.service import read_and_import_rows as import_services
from bc211.import_open_referral_csv.address import read_and_import_rows as import_addresses
from bc211.import_open_referral_csv.taxonomy import read_and_import_rows as import_taxonomy_terms
from bc211.import_open_referral_csv.service_taxonomy import read_and_import_rows as import_service_taxonomy
from human_services.organizations.models import Organization
from human_services.services.models import Service
from human_services.addresses.models import Address
from taxonomies.models import TaxonomyTerm
from bc211.convert_icarol_csv.tests.helpers import Bc211CsvDataBuilder, TestDataSink
from bc211.convert_icarol_csv.parser import parse
from common.testhelpers.random_test_values import a_string
from human_services.locations.models import Location


class EndToEndTest(TestCase):

    def test_service_with_mailing_and_physical_address(self):
        the_organization_id = a_string()
        the_service_id = a_string()
        physical_address_1 = a_string()
        physical_city = a_string()
        mailing_address_1 = a_string()
        mailing_city = a_string()
        the_region = a_string()

        # create and parse the bc211 csv data for a service with mailing and physical address

        bc211_csv_data = (Bc211CsvDataBuilder().
                          as_organization().
                          with_field('ResourceAgencyNum', the_organization_id).
                          with_field('PublicName', a_string()).
                          next_row().
                          as_service().
                          with_field('ResourceAgencyNum', the_service_id).
                          with_field('PublicName', a_string()).
                          with_field('ParentAgencyNum', the_organization_id).
                          with_field('MailingAddress1', mailing_address_1).
                          with_field('MailingAddress2', a_string()).
                          with_field('MailingAddress3', a_string()).
                          with_field('MailingCity', mailing_city).
                          with_field('MailingStateProvince', a_string()).
                          with_field('MailingCountry', 'CA').
                          with_field('PhysicalAddress1', physical_address_1).
                          with_field('PhysicalAddress2', a_string()).
                          with_field('PhysicalAddress3', a_string()).
                          with_field('PhysicalCity', physical_city).
                          with_field('PhysicalStateProvince', a_string()).
                          with_field('PhysicalCountry', 'CA').
                          build())
        parsed_data = parse(TestDataSink(), bc211_csv_data, the_region)

        self.assertEqual(len(parsed_data.organizations), 1)
        self.assertEqual(parsed_data.organizations[0]['id'], f'{the_organization_id}_{the_region}')

        self.assertEqual(len(parsed_data.services), 1)
        self.assertEqual(parsed_data.services[0]['organization_id'], f'{the_organization_id}_{the_region}')
        self.assertEqual(parsed_data.services[0]['id'], f'{the_service_id}_{the_region}')

        self.assertEqual(len(parsed_data.locations), 2)
        location_id = parsed_data.locations[0]['id']

        addresses = parsed_data.addresses
        self.assertEqual(len(addresses), 2)
        if addresses[0]['type'] == 'physical_address':
            physical_address = addresses[0]
            mailing_address = addresses[1]
        else:
            mailing_address = addresses[0]
            physical_address = addresses[1]

        self.assertNotEqual(physical_address['id'], mailing_address['id'])
        self.assertEqual(physical_address['address_1'], physical_address_1)
        self.assertEqual(mailing_address['address_1'], mailing_address_1)

        # import organization

        open_referral_csv_data = [[
            # id,name,alternate_name,
            r['id'], r['name'], r['alternate_name'],
            # description,email,url,
            '', '', '',
            # tax_status,tax_id,year_incorporated,legal_status
            '', '', '', '']
                for r in parsed_data.organizations]
        organization_id_with_region = f'{the_organization_id}_{the_region}'
        collector = InactiveRecordsCollector()
        counters = ImportCounters()
        import_organization(open_referral_csv_data, collector, counters)
        result_from_db = Organization.objects.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, organization_id_with_region)

        # import location

        open_referral_csv_data = [[
            # id,organization_id,name,
            r['id'], organization_id_with_region, r['name'],
            # alternate_name,description,transportation,
            '', '', '',
            # latitude,longitude
            0, 0]
                for r in parsed_data.locations]
        import_locations(open_referral_csv_data, collector, counters)
        result_from_db = Location.objects.all()
        self.assertEqual(len(result_from_db), 2)

        # import service

        open_referral_csv_data = [[
            # id,organization_id,program_id,
            r['id'], r['organization_id'], '',
            # name,alternate_name,description,
            r['name'], r['alternate_name'], '',
            # url,email,status,
            r['url'], r['email'], '',
            # interpretation_services,application_process,wait_time,
            '', '', '',
            # fees,accreditations,licenses, taxonomy_ids,last_verified_on-x
            '', '', '', '', '']
                for r in parsed_data.services]
        import_services(open_referral_csv_data, collector, counters)
        result_from_db = Service.objects.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, f'{the_service_id}_{the_region}')
        self.assertEqual(result_from_db[0].organization_id, organization_id_with_region)

        # import addresses

        open_referral_csv_data = [[
            # id,type,location_id,
            r['id'], r['type'], location_id,
            # attention,address_1,address_2,
            '', r['address_1'], r['address_2'],
            # address_3,address_4,city,
            r['address_3'], '', r['city'],
            # region,state_province, postal_code,
            '', r['state_province'], '',
            # country
            r['country']]
                for r in parsed_data.addresses]
        import_addresses(open_referral_csv_data, collector, counters)
        result_from_db = Address.objects.all()
        self.assertEqual(len(result_from_db), 2)

        if result_from_db[0].city == mailing_city:
            mailing_address = result_from_db[0]
            physical_address = result_from_db[1]
        else:
            physical_address = result_from_db[0]
            mailing_address = result_from_db[1]

        self.assertEqual(physical_address.address[0:20], physical_address_1[0:20])
        self.assertEqual(physical_address.city, physical_city)
        self.assertEqual(mailing_address.address[0:20], mailing_address_1[0:20])
        self.assertEqual(mailing_address.city, mailing_city)

    def test_two_services_with_the_same_address(self):
        first_organization_id = a_string()
        second_organization_id = a_string()
        first_service_id = a_string()
        second_service_id = a_string()
        first_name = a_string()
        second_name = a_string()
        mailing_address_1 = a_string()
        mailing_city = a_string()
        the_region = a_string()

        # create and parse the bc211 csv data for two services with the same address information

        bc211_csv_data = (Bc211CsvDataBuilder().
                          as_organization().
                          with_field('ResourceAgencyNum', first_organization_id).
                          with_field('PublicName', first_name).
                          next_row().
                          as_organization().
                          with_field('ResourceAgencyNum', second_organization_id).
                          with_field('PublicName', second_name).
                          next_row().
                          as_service().
                          with_field('ResourceAgencyNum', first_service_id).
                          # Having the same name on the organization and service ensures that the organization and
                          # service locations end up with the same properties, including the name, hence the same
                          # hash, hence only one location record will be shared by both.
                          with_field('PublicName', first_name).
                          with_field('ParentAgencyNum', first_organization_id).
                          with_field('MailingAddress1', mailing_address_1).
                          with_field('MailingCity', mailing_city).
                          with_field('MailingCountry', 'CA').
                          next_row().
                          as_service().
                          with_field('ResourceAgencyNum', second_service_id).
                          with_field('PublicName', second_name).
                          with_field('ParentAgencyNum', second_organization_id).
                          with_field('MailingAddress1', mailing_address_1).
                          with_field('MailingCity', mailing_city).
                          with_field('MailingCountry', 'CA').
                          build())
        parsed_data = parse(TestDataSink(), bc211_csv_data, the_region)

        self.assertEqual(len(parsed_data.organizations), 2)
        self.assertEqual(parsed_data.organizations[0]['id'], f'{first_organization_id}_{the_region}')
        self.assertEqual(parsed_data.organizations[1]['id'], f'{second_organization_id}_{the_region}')

        self.assertEqual(len(parsed_data.services), 2)
        self.assertEqual(parsed_data.services[0]['id'], f'{first_service_id}_{the_region}')
        self.assertEqual(parsed_data.services[1]['id'], f'{second_service_id}_{the_region}')
        self.assertEqual(parsed_data.services[0]['organization_id'], f'{first_organization_id}_{the_region}')
        self.assertEqual(parsed_data.services[1]['organization_id'], f'{second_organization_id}_{the_region}')

        self.assertEqual(len(parsed_data.locations), 2)
        self.assertEqual(parsed_data.locations[0]['name'], first_name)
        self.assertEqual(parsed_data.locations[1]['name'], second_name)
        # the name for the location may come from the service or the organization, no need to
        # nail this down currently since doing so would make the parser quite a lot more complex
        # for no tangible benefit.

        self.assertEqual(len(parsed_data.addresses), 2)
        self.assertNotEqual(parsed_data.addresses[0]['id'], parsed_data.addresses[1]['id'])
        self.assertEqual(parsed_data.addresses[0]['address_1'], mailing_address_1)
        self.assertEqual(parsed_data.addresses[1]['address_1'], mailing_address_1)
        self.assertEqual(parsed_data.addresses[0]['location_id'], parsed_data.locations[0]['id'])
        self.assertEqual(parsed_data.addresses[1]['location_id'], parsed_data.locations[1]['id'])

        # import organization

        open_referral_csv_data = [[
            # id,name,alternate_name,
            r['id'], r['name'], r['alternate_name'],
            # description,email,url,
            '', '', '',
            # tax_status,tax_id,year_incorporated,legal_status
            '', '', '', '']
                for r in parsed_data.organizations]
        collector = InactiveRecordsCollector()
        counters = ImportCounters()
        import_organization(open_referral_csv_data, collector, counters)
        result_from_db = Organization.objects.all()
        self.assertEqual(len(result_from_db), 2)
        self.assertEqual({r.id for r in result_from_db}, {
            f'{first_organization_id}_{the_region}', f'{second_organization_id}_{the_region}' })

        # import location

        open_referral_csv_data = [[
            # id,organization_id,name,
            r['id'], f'{first_organization_id}_{the_region}', r['name'],
            # alternate_name,description,transportation,
            '', '', '',
            # latitude,longitude
            0, 0]
                for r in parsed_data.locations]
        import_locations(open_referral_csv_data, collector, counters)
        result_from_db = Location.objects.all()
        self.assertEqual(len(result_from_db), 2)
        self.assertEqual({r.name for r in result_from_db}, {first_name, second_name})

        # import service

        open_referral_csv_data = [[
            # id,organization_id,program_id,
            r['id'], r['organization_id'], '',
            # name,alternate_name,description,
            r['name'], r['alternate_name'], '',
            # url,email,status,
            r['url'], r['email'], '',
            # interpretation_services,application_process,wait_time,
            '', '', '',
            # fees,accreditations,licenses, taxonomy_ids,last_verified_on-x
            '', '', '', '', '']
                for r in parsed_data.services]
        import_services(open_referral_csv_data, collector, counters)
        result_from_db = Service.objects.all()
        self.assertEqual(len(result_from_db), 2)
        self.assertEqual({r.id for r in result_from_db}, {f'{first_service_id}_{the_region}',
                                                          f'{second_service_id}_{the_region}'})
        self.assertEqual({r.organization_id for r in result_from_db}, {f'{first_organization_id}_{the_region}',
                                                                       f'{second_organization_id}_{the_region}'})

        # import addresses

        open_referral_csv_data = [[
            # id,type,location_id,
            r['id'], r['type'], r['location_id'],
            # attention,address_1,address_2,
            '', r['address_1'], '',
            # address_3,address_4,city,
            '', '', r['city'],
            # region,state_province, postal_code,
            '', '', '',
            # country
            r['country']]
                for r in parsed_data.addresses]
        import_addresses(open_referral_csv_data, collector, counters)
        result_from_db = Address.objects.all()
        self.assertEqual(len(result_from_db), 2)
        self.assertEqual(result_from_db[0].address[0:20], mailing_address_1[0:20])
        self.assertEqual(result_from_db[1].address[0:20], mailing_address_1[0:20])

    def test_service_with_taxonomy_term(self):
        # all upper case taxonomy terms are by convention assigned the bc211-what taxonomy
        bc211_what_taxonomy_term = a_string().upper()
        the_organization_id = a_string()
        the_service_id = a_string()
        the_region = a_string()

        # create and parse the bc211 csv data for a service with a taxonomy term

        bc211_csv_data = (Bc211CsvDataBuilder().
                          as_organization().
                          with_field('ResourceAgencyNum', the_organization_id).
                          with_field('PublicName', a_string()).
                          next_row().
                          as_service().
                          with_field('ResourceAgencyNum', the_service_id).
                          with_field('PublicName', a_string()).
                          with_field('ParentAgencyNum', the_organization_id).
                          with_field('TaxonomyTerm', bc211_what_taxonomy_term).
                          build())
        parsed_data = parse(TestDataSink(), bc211_csv_data, the_region)

        self.assertEqual(len(parsed_data.organizations), 1)
        self.assertEqual(parsed_data.organizations[0]['id'], f'{the_organization_id}_{the_region}')

        self.assertEqual(len(parsed_data.services), 1)
        self.assertEqual(parsed_data.services[0]['organization_id'], f'{the_organization_id}_{the_region}')
        self.assertEqual(parsed_data.services[0]['id'], f'{the_service_id}_{the_region}')

        self.assertEquals(len(parsed_data.taxonomy_terms), 1)
        self.assertEquals(parsed_data.taxonomy_terms[0]['name'], bc211_what_taxonomy_term.lower())
        self.assertEquals(parsed_data.taxonomy_terms[0]['vocabulary'], 'bc211-what')
        taxonomy_term_id = parsed_data.taxonomy_terms[0]['id']

        self.assertEquals(len(parsed_data.services_taxonomy), 1)
        self.assertEquals(parsed_data.services_taxonomy[0]['service_id'], f'{the_service_id}_{the_region}')
        self.assertEquals(parsed_data.services_taxonomy[0]['taxonomy_id'], taxonomy_term_id)

        # import organization

        open_referral_csv_data = [[
            # id,name,alternate_name,
            r['id'], r['name'], r['alternate_name'],
            # description,email,url,
            '', '', '',
            # tax_status,tax_id,year_incorporated,legal_status
            '', '', '', '']
                for r in parsed_data.organizations]
        collector = InactiveRecordsCollector()
        counters = ImportCounters()
        import_organization(open_referral_csv_data, collector, counters)
        result_from_db = Organization.objects.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, f'{the_organization_id}_{the_region}')

        # import service

        open_referral_csv_data = [[
            # id,organization_id,program_id,
            r['id'], r['organization_id'], '',
            # name,alternate_name,description,
            r['name'], r['alternate_name'], '',
            # url,email,status,
            r['url'], r['email'], '',
            # interpretation_services,application_process,wait_time,
            '', '', '',
            # fees,accreditations,licenses, taxonomy_ids,last_verified_on-x
            '', '', '', '', '']
                for r in parsed_data.services]
        import_services(open_referral_csv_data, collector, counters)
        result_from_db = Service.objects.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, f'{the_service_id}_{the_region}')
        self.assertEqual(result_from_db[0].organization_id, f'{the_organization_id}_{the_region}')

        # import taxonomy terms

        open_referral_csv_data = [[
            # id,name,parent_id,
            r['id'], r['name'], '',
            # parent_name,vocabulary
            '', r['vocabulary']]
                for r in parsed_data.taxonomy_terms]
        import_taxonomy_terms(open_referral_csv_data, counters)
        result_from_db = TaxonomyTerm.objects.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, taxonomy_term_id)
        self.assertEqual(result_from_db[0].name, bc211_what_taxonomy_term.lower())
        self.assertEqual(result_from_db[0].taxonomy_id, 'bc211-what')

        # import service taxonomy terms

        open_referral_csv_data = [[
            # id,service_id,taxonomy_id, taxonomy_detail
            r['id'], r['service_id'], r['taxonomy_id'], '']
                for r in parsed_data.services_taxonomy]
        import_service_taxonomy(open_referral_csv_data, collector)
        result_from_db = Service.objects.all()[0].taxonomy_terms.all()
        self.assertEqual(len(result_from_db), 1)
        self.assertEqual(result_from_db[0].id, taxonomy_term_id)
        self.assertEqual(result_from_db[0].taxonomy_id, 'bc211-what')
        self.assertEqual(result_from_db[0].name, bc211_what_taxonomy_term.lower())
