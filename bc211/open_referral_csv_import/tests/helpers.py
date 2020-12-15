from datetime import date
import string
from common.testhelpers.random_test_values import (a_string, an_email_address, a_website_address,
                                a_latitude, a_longitude, a_phone_number)


class OpenReferralCsvOrganizationBuilder:
    def __init__(self):
        self.organization_id = a_string()
        self.name = a_string()
        self.alternate_name = a_string()
        self.description = a_string()
        self.email = an_email_address()
        self.url = a_website_address()

    def with_id(self, organization_id):
        self.organization_id = organization_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_alternate_name(self, alternate_name):
        self.alternate_name = alternate_name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_email(self, email):
        self.email = email
        return self

    def with_url(self, url):
        self.url = url
        return self

    def build(self):
        not_used_tax_status = ''
        not_used_tax_id = ''
        not_used_year_incorporated = ''
        not_used_legal_status = ''
        return [self.organization_id, self.name, self.alternate_name, self.description, 
            self.email, self.url, not_used_tax_status, not_used_tax_id, 
            not_used_year_incorporated, not_used_legal_status]


class OpenReferralCsvServiceBuilder:
    def __init__(self, organization):
        self.service_id = a_string()
        self.organization_id = organization.id
        self.name = a_string()
        self.alternate_name = a_string()
        self.description = a_string()
        self.url = a_website_address()
        self.email = an_email_address()
        self.last_verified_on = date.today().strftime("%Y-%m-%d")

    def with_id(self, service_id):
        self.service_id = service_id
        return self

    def with_organization_id(self, organization_id):
        self.organization_id = organization_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_alternate_name(self, alternate_name):
        self.alternate_name = alternate_name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_url(self, url):
        self.url = url
        return self

    def with_email(self, email):
        self.email = email
        return self

    def with_last_verified_on(self, last_verified_on):
        self.last_verified_on = last_verified_on
        return self

    def build(self):
        not_used_program_id = ''
        not_used_status = ''
        not_used_intepretation_services = ''
        not_used_application_process = ''
        not_used_wait_time = ''
        not_used_fees = ''
        not_used_accreditations = ''
        not_used_licenses = ''
        not_used_taxonomy_ids = ''
        return [self.service_id, self.organization_id, not_used_program_id, self.name,
            self.alternate_name, self.description, self.url, self.email, not_used_status,
            not_used_intepretation_services, not_used_application_process, not_used_wait_time,
            not_used_fees, not_used_accreditations, not_used_licenses, not_used_taxonomy_ids,
            self.last_verified_on]
  

class OpenReferralCsvLocationBuilder:
    def __init__(self, organization):
        self.location_id = a_string()
        self.organization_id = organization.id
        self.name = a_string()
        self.alternate_name = a_string()
        self.description = a_string()
        self.latitude = str(a_latitude())
        self.longitude = str(a_longitude())

    def with_id(self, location_id):
        self.location_id = location_id
        return self

    def with_organization_id(self, organization_id):
        self.organization_id = organization_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_alternate_name(self, alternate_name):
        self.alternate_name = alternate_name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_latitude(self, latitude):
        self.latitude = latitude
        return self

    def with_longitude(self, longitude):
        self.longitude = longitude
        return self

    def build(self):
        not_used_transportation = ''
        return [self.location_id, self.organization_id, self.name, self.alternate_name,
                self.description, not_used_transportation, self.latitude, self.longitude]


class OpenReferralCsvServiceAtLocationBuilder:
    def __init__(self, service, location):
        self.service_id = service.id
        self.location_id = location.id

    def with_service_id(self, service_id):
        self.service_id = service_id
        return self

    def with_location_id(self, location_id):
        self.location_id = location_id
        return self

    def build(self):
        not_used_id = ''
        not_used_description = ''
        return [not_used_id, self.service_id, self.location_id, not_used_description]


class OpenReferralCsvAddressBuilder:
    def __init__(self, location):
        self.address_id = a_string()
        self.address_type = 'physical_address'
        self.location_id = location.id
        self.attention = a_string()
        self.address_1 = a_string()
        self.address_2 = ''
        self.address_3 = ''
        self.address_4 = ''
        self.city = a_string()
        self.state_province = a_string()
        self.postal_code = a_string()
        self.country = a_string(2, string.ascii_uppercase)

    def with_address_id(self, address_id):
        self.address_id = address_id
        return self

    def with_address_type(self, address_type):
        self.address_type = address_type
        return self

    def with_location_id(self, location_id):
        self.location_id = location_id

    def with_attention(self, attention):
        self.attention = attention
        return self

    def with_address_1(self, address_1):
        self.address_1 = address_1
        return self

    def with_address_2(self, address_2):
        self.address_2 = address_2
        return self

    def with_address_3(self, address_3):
        self.address_3 = address_3
        return self

    def with_address_4(self, address_4):
        self.address_4 = address_4
        return self

    def with_city(self, city):
        self.city = city
        return self

    def with_state_province(self, state_province):
        self.state_province = state_province
        return self

    def with_postal_code(self, postal_code):
        self.postal_code = postal_code
        return self

    def with_country(self, country):
        self.country = country
        return self

    def build(self):
        not_used_region = ''
        return [self.address_id, self.address_type, self.location_id, self.attention,
            self.address_1, self.address_2, self.address_3, self.address_4,
            self.city, not_used_region, self.state_province, self.postal_code, self.country]


class OpenReferralCsvPhoneBuilder:
    def __init__(self, location):
        self.location_id = location.id
        self.number = a_phone_number()
        self.phone_type = a_string()

    def with_location_id(self, location_id):
        self.location_id = location_id
        return self

    def with_number(self, number):
        self.number = number
        return self

    def with_phone_type(self, phone_type):
        self.phone_type = phone_type
        return self

    def build(self):
        not_used_id = ''
        not_used_service_id = ''
        not_used_organization_id = ''
        not_used_contact_id = ''
        not_used_service_at_location_id = ''
        not_used_extension = ''
        not_used_language = ''
        not_used_description = ''
        not_used_department = ''
        return [not_used_id, self.location_id, not_used_service_id, not_used_organization_id,
            not_used_contact_id, not_used_service_at_location_id, self.number,
            not_used_extension, self.phone_type, not_used_language, not_used_description,
            not_used_department]


class OpenReferralCsvTaxonomyBuilder:
    def __init__(self):
        self.taxonomy_id = a_string()
        self.name = a_string()

    def with_taxonomy_id(self, taxonomy_id):
        self.taxonomy_id = taxonomy_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def build(self):
        not_used_parent_id = ''
        not_used_parent_name = ''
        not_used_vocabulary = ''
        return [self.taxonomy_id, self.name, not_used_parent_id, not_used_parent_name,
            not_used_vocabulary]


class OpenReferralCsvServiceTaxonomyBuilder:
    def __init__(self):
        self.service_id = a_string()
        self.taxonomy_id = a_string()

    def with_service_id(self, service_id):
        self.service_id = service_id
        return self

    def with_taxonomy_id(self, taxonomy_id):
        self.taxonomy_id = taxonomy_id
        return self

    def build(self):
        not_used_id = ''
        not_used_taxonomy_detail = ''
        return [not_used_id, self.service_id, self.taxonomy_id, not_used_taxonomy_detail]
