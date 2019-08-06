from django.core.exceptions import ValidationError
import itertools
import logging
import re
import xml.etree.ElementTree as etree
from urllib import parse as urlparse

from bc211 import dtos
from bc211.exceptions import MissingRequiredFieldXmlParseException

import html
from html.parser import HTMLParser

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
        field_text = parent.find(field).text
        return remove_double_escaped_html_markup(field_text)
    except AttributeError:
        raise MissingRequiredFieldXmlParseException('Missing required field: "{0}"'.format(field))


def parse_optional_field(parent, field):
    value = parent.find(field)
    if value is None:
        return None
    return remove_double_escaped_html_markup(value.text)


def parse_agency_name(agency):
    return parse_required_field(agency, 'Name')


def parse_agency_description(agency):
    return parse_optional_field(agency, 'AgencyDescription')


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
    physical_address = parse_physical_address(site, id)
    postal_address = parse_postal_address(site, id)
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
    return parse_optional_field(service, 'Description')


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


def parse_physical_address(site_xml, site_id):
    physical_address = site_xml.find('PhysicalAddress')
    if physical_address:
        return parse_address(physical_address, site_id, 'physical_address')
    return None


def parse_postal_address(site_xml, site_id):
    postal_address = site_xml.find('MailingAddress')
    if postal_address:
        return parse_address(postal_address, site_id, 'postal_address')
    return None


def parse_address(address, site_id, address_type_id):
    city = parse_city(address)
    if not city:
        return None
    country = parse_country(address)
    if not country:
        return None
    return dtos.Address(location_id=site_id, address_type_id=address_type_id, city=city,
                        country=country, address_lines=parse_address_lines(address),
                        state_province=parse_state_province(address),
                        postal_code=parse_postal_code(address))


def parse_address_lines(address):
    sorted_address_children = sorted(address.getchildren(), key=lambda child: child.tag)
    address_line_tags = [child.tag for child in sorted_address_children if re.match('Line[1-9]', child.tag)]
    if not address_line_tags:
        return None
    address_line_tag_values = [parse_optional_field(address, tag) for tag in address_line_tags]
    if not address_line_tag_values:
        return None
    non_empty_address_lines = [address_line for address_line in address_line_tag_values if address_line]
    if not non_empty_address_lines:
        return None
    return '\n'.join(non_empty_address_lines)


def parse_city(address):
    return parse_optional_field(address, 'City')


def parse_country(address):
    country = parse_optional_field(address, 'Country')
    if country == 'Canada':
        return 'CA'
    if country == 'United States':
        return 'US'
    if country is None:
        return None
    if len(country) > 2:
        return None
    return country


def parse_state_province(address):
    return parse_optional_field(address, 'State')


def parse_postal_code(address):
    return parse_optional_field(address, 'ZipCode')


def parse_site_phone_number_list(site, site_id):
    valid_phones = filter(phone_has_number_and_type, site.findall('Phone'))
    return [parse_site_phone(phone, site_id) for phone in valid_phones]


def parse_site_phone(phone, site_id):
    location_id = site_id
    phone_number_type_id = convert_phone_type_to_type_id(phone.find('Type').text)
    phone_number = clean_phone_number(phone.find('PhoneNumber').text)
    return dtos.PhoneAtLocation(
        location_id=location_id,
        phone_number_type_id=phone_number_type_id,
        phone_number=phone_number
    )

def clean_one_phone_number(phone_number):
    phone_number = re.sub(r'([Ll]ocal|[Ee]xt)[ \d].*', '', phone_number)
    if re.search(r'[a-zA-Z]', phone_number):
        phone_number = re.sub(r'[a-cA-C]', '2', phone_number)
        phone_number = re.sub(r'[d-fD-F]', '3', phone_number)
        phone_number = re.sub(r'[g-iG-I]', '4', phone_number)
        phone_number = re.sub(r'[j-lJ-L]', '5', phone_number)
        phone_number = re.sub(r'[m-oM-O]', '6', phone_number)
        phone_number = re.sub(r'[p-sP-S]', '7', phone_number)
        phone_number = re.sub(r'[t-vT-V]', '8', phone_number)
        phone_number = re.sub(r'[w-zW-Z]', '9', phone_number)
        phone_number = re.sub(r'(\(?.*\)?.*)(\(.*\))', r'\1', phone_number)
    phone_number = re.sub(r'[- \(\)]', '', phone_number)
    if re.search(r'\d{11}', phone_number):
        phone_number = re.sub(r'(\d)(\d{3})(\d{3})(\d{4})', r'\1-\2-\3-\4', phone_number)
        return phone_number
    if re.search(r'\d{10}', phone_number):
        phone_number = re.sub(r'(\d{3})(\d{3})(\d{4})', r'\1-\2-\3', phone_number)
        return phone_number
    return phone_number

def clean_multiple_phone_numbers(phone_number):
    toll_free_format = r'1-8[\d]{2}-[\d]{3}-[\d]{4}'
    phone_number_array = re.split("/|or|;", phone_number)
    for index in range(len(phone_number_array)):
        cleanedNumber = clean_one_phone_number(phone_number_array[index])
        if re.search(toll_free_format, cleanedNumber):
            return cleanedNumber
    return cleanedNumber

def clean_phone_number(phone_number):
    if re.search(r'/|or|;', phone_number):
        return clean_multiple_phone_numbers(phone_number)
    return clean_one_phone_number(phone_number)

def phone_has_number_and_type(phone):
    return parse_optional_field(phone, 'PhoneNumber') and parse_optional_field(phone, 'Type')


def convert_phone_type_to_type_id(phone_type):
    return phone_type.lower().replace(' ', '_')


def remove_double_escaped_html_markup(data):
    if data is None:
        return None

    unescaped_once = html.unescape(data)
    unescaped_twice = html.unescape(unescaped_once)

    remover = HTMLRemover()
    remover.feed(unescaped_twice)
    return remover.get_data()


class HTMLRemover(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = False
        self.handled_data = []

    def handle_data(self, data):
        self.handled_data.append(data)

    def get_data(self):
        return ''.join(self.handled_data)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def error(self, message):
        raise RuntimeError(message)
