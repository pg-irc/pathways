from django.core.exceptions import ValidationError
import itertools
import logging
import re
import xml.etree.ElementTree as etree
from urllib import parse as urlparse
from phonenumber_field.validators import validate_international_phonenumber

from bc211 import dtos
from bc211.exceptions import MissingRequiredFieldXmlParseException

LOGGER = logging.getLogger(__name__)

def read_records_from_file(file):
    xml = file.read()
    return parse(xml)

def parse(xml_data_as_string):
    root_xml = etree.fromstring(xml_data_as_string)
    agencies = root_xml.findall('Agency')
    return map(parse_agency, agencies)

def parse_agency(agency):
    id = parse_agency_key(agency)
    name = parse_agency_name(agency)
    description = parse_agency_description(agency)
    website = parse_agency_website_with_prefix(agency)
    email = parse_agency_email(agency)
    LOGGER.debug('Organization "%s" "%s"', id, name)
    locations = parse_sites(agency, id)
    return dtos.Organization(id=id, name=name, description=description, website=website,
                             email=email, locations=locations)

def parse_agency_key(agency):
    return parse_required_field(agency, 'Key')

def parse_required_field(parent, field):
    try:
        return parent.find(field).text
    except AttributeError:
        raise MissingRequiredFieldXmlParseException('Missing required field: "{0}"'.format(field))

def parse_optional_field(parent, field):
    value = parent.find(field)
    return None if value is None else value.text

def parse_agency_name(agency):
    return parse_required_field(agency, 'Name')

def parse_agency_description(agency):
    return parse_required_field(agency, 'AgencyDescription')

def parse_agency_email(agency):
    return parse_optional_field(agency, 'Email/Address')

def parse_agency_website_with_prefix(agency):
    website = parse_optional_field(agency, 'URL/Address')
    return None if website is None else website_with_http_prefix(website)

def website_with_http_prefix(website):
    parts = urlparse.urlparse(website, 'http')
    whole_with_extra_slash = urlparse.urlunparse(parts)
    return whole_with_extra_slash.replace('///', '//')

def parse_sites(agency, organization_id):
    sites = agency.findall('Site')
    return map(SiteParser(organization_id), sites)

class SiteParser:
    def __init__(self, organization_id):
        self.organization_id = organization_id

    def __call__(self, site):
        return parse_site(site, self.organization_id)

def parse_site(site, organization_id):
    id = parse_site_id(site)
    name = parse_site_name(site)
    description = parse_site_description(site)
    spatial_location = parse_spatial_location_if_defined(site)
    services = parse_service_list(site, organization_id, id)
    physical_address = parse_physical_address(site, id, name)
    postal_address = parse_postal_address(site, id, name)
    phone_numbers = parse_site_phone_number_list(site, id)
    LOGGER.debug('Location: %s %s', id, name)
    return dtos.Location(id=id, name=name, organization_id=organization_id,
                         description=description, spatial_location=spatial_location,
                         services=services, physical_address=physical_address,
                         postal_address=postal_address, phone_numbers=phone_numbers)

def parse_site_id(site):
    return parse_required_field(site, 'Key')

def parse_site_name(site):
    return parse_required_field(site, 'Name')

def parse_site_description(site):
    return parse_required_field(site, 'SiteDescription')

def parse_spatial_location_if_defined(site):
    latitude = parse_optional_field(site, 'SpatialLocation/Latitude')
    longitude = parse_optional_field(site, 'SpatialLocation/Longitude')
    if latitude is None or longitude is None:
        return None
    return dtos.SpatialLocation(latitude=latitude, longitude=longitude)

def parse_service_list(site, organization_id, site_id):
    services = site.findall('SiteService')
    return list(map(ServiceParser(organization_id, site_id), services))

class ServiceParser:
    def __init__(self, organization_id, site_id):
        self.organization_id = organization_id
        self.site_id = site_id

    def __call__(self, service):
        return parse_service(service, self.organization_id, self.site_id)

def parse_service(service, organization_id, site_id):
    id = parse_service_id(service)
    name = parse_service_name(service)
    description = parse_service_description(service)
    taxonomy_terms = parse_service_taxonomy_terms(service, id)
    LOGGER.debug('Service: "%s" "%s"', id, name)
    return dtos.Service(id=id, name=name, organization_id=organization_id,
                        site_id=site_id, description=description,
                        taxonomy_terms=taxonomy_terms)

def parse_service_id(service):
    return parse_required_field(service, 'Key')

def parse_service_name(service):
    return parse_required_field(service, 'Name')

def parse_service_description(service):
    return parse_required_field(service, 'Description')

def parse_service_taxonomy_terms(service, service_id):
    taxonomy_terms = service.findall('Taxonomy')
    return itertools.chain.from_iterable(
        map(ServiceTaxonomyTermParser(service_id), taxonomy_terms)
    )

class ServiceTaxonomyTermParser:
    def __init__(self, service_id):
        self.service_id = service_id

    def __call__(self, service_taxonomy_term):
        return parse_service_taxonomy_term(service_taxonomy_term, self.service_id)

def parse_service_taxonomy_term(service_taxonomy_term, service_id):
    code = parse_required_field(service_taxonomy_term, 'Code')

    LOGGER.debug('Taxonomy term "%s"', code)

    if code and is_bc211_taxonomy_term(code):
        yield from parse_bc211_taxonomy_term(code)
    elif code:
        yield from parse_airs_taxonomy_term(code)

def is_bc211_taxonomy_term(code_str):
    return code_str.startswith('{')

def parse_bc211_taxonomy_term(code_str):
    bc211_json_re = r"(\w+)\:\'([^\']+)\'"
    groups = re.findall(bc211_json_re, code_str)
    for (taxonomy_id, name) in groups:
        full_taxonomy_id = 'bc211-{}'.format(taxonomy_id)
        yield dtos.TaxonomyTerm(taxonomy_id=full_taxonomy_id, name=name)

def parse_airs_taxonomy_term(code_str):
    taxonomy_id = 'airs'
    yield dtos.TaxonomyTerm(taxonomy_id=taxonomy_id, name=code_str)

def parse_physical_address(site_xml, site_id, site_name):
    type_id = 'physical_address'
    return parse_address_and_handle_errors(site_xml.find('PhysicalAddress'), site_id, site_name, type_id)

def parse_postal_address(site_xml, site_id, site_name):
    type_id = 'postal_address'
    return parse_address_and_handle_errors(site_xml.find('MailingAddress'), site_id, site_name, type_id)

def parse_address_and_handle_errors(address, site_id, site_name, address_type_id):
    try:
        return parse_address(address, site_id, address_type_id)
    except MissingRequiredFieldXmlParseException as error:
        LOGGER.warning('Failed to parse address for\n\tlocation %s (%s):\n\t%s',
                       site_id, site_name, error)
    return None

def parse_address(address, site_id, address_type_id):
    if not address:
        raise MissingRequiredFieldXmlParseException('No {} element found'.format(address_type_id))
    address_lines = parse_address_lines(address)
    city = parse_city(address)
    country = parse_country(address)
    if not address_lines or not city or not country:
        message = 'Parsed "{}" for address, "{}" for city, and "{}" for country.'.format(address_lines, city, country)
        raise MissingRequiredFieldXmlParseException(message)

    state_province = parse_state_province(address)
    postal_code = parse_postal_code(address)
    return dtos.Address(location_id=site_id, address_lines=address_lines,
                        city=city, state_province=state_province, postal_code=postal_code,
                        country=country, address_type_id=address_type_id)

def parse_address_lines(address):
    line_1 = parse_required_field(address, 'Line1')
    if not line_1:
        return None
    address_lines = [line_1]
    address_children = sorted(address.getchildren(), key=lambda child: child.tag)
    for child in address_children:
        if re.match("Line[2-4]", child.tag):
            address_line = parse_required_field(address, child.tag)
            address_lines.append(address_line)
        if re.match("Line[5-9]", child.tag):
            LOGGER.warning('Tag %s encountered and has not been parsed.', child.tag)
    return '\n'.join(address_lines)

def parse_city(address):
    return parse_required_field(address, 'City')

def parse_country(address):
    return parse_required_field(address, 'Country')

def parse_state_province(address):
    return parse_optional_field(address, 'State')

def parse_postal_code(address):
    return parse_optional_field(address, 'ZipCode')

def parse_site_phone_number_list(site, site_id):
    valid_phones = filter(phone_has_valid_number_and_type, site.findall('Phone'))
    return [parse_site_phone(phone, site_id) for phone in valid_phones]

def parse_site_phone(phone, site_id):
    location_id = site_id
    phone_number_type_id = convert_phone_type_to_type_id(phone.find('Type').text)
    phone_number = convert_bc_phone_number_to_international(phone.find('PhoneNumber').text)
    return dtos.PhoneNumber(
        location_id=location_id,
        phone_number_type_id=phone_number_type_id,
        phone_number=phone_number
    )

def phone_has_valid_number_and_type(phone):
    phone_number = parse_optional_field(phone, 'PhoneNumber')
    phone_number_type = parse_optional_field(phone, 'Type')
    if not (phone_number and phone_number_type):
        return False
    return is_valid_phone_number(phone_number)

def is_valid_phone_number(phone_number):
    try:
        intl_phone_number = convert_bc_phone_number_to_international(phone_number)
    except ValueError:
        LOGGER.warning('Failed to parse value: "%s" for phone number.', phone_number)
        return False
    try:
        validate_international_phonenumber(intl_phone_number)
    except ValidationError:
        LOGGER.warning('Failed to parse value: "%s" for international phone number.', intl_phone_number)
        return False
    return True

def convert_phone_type_to_type_id(phone_type):
    return phone_type.lower().replace(' ', '_')

def convert_bc_phone_number_to_international(bc_phone_number):
    dashes_replaced = bc_phone_number.replace('-', '')
    return int(dashes_replaced) if dashes_replaced[0] == '1' else int('1' + dashes_replaced)
