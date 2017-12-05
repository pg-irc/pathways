import logging
import xml.etree.ElementTree as etree
from urllib import parse as urlparse
from bc211 import dtos

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
    website = parse_agency_website(agency)
    email = parse_agency_email(agency)
    LOGGER.info('Parsed organization: %s %s', id, name)
    locations = parse_sites(agency, id)
    return dtos.Organization(id, name, description, website, email, locations)

def parse_agency_key(agency):
    return agency.find('Key').text

def parse_agency_name(agency):
    return agency.find('Name').text

def parse_agency_description(agency):
    return agency.find('AgencyDescription').text

def parse_agency_email(agency):
    email = agency.find('Email/Address')
    return None if email is None else email.text

def parse_agency_website(agency):
    website = agency.find('URL/Address')
    if website is None:
        return None
    return website_with_http_prefix(website.text)

def website_with_http_prefix(website):
    parts = urlparse.urlparse(website, 'http')
    url_with_extra_slash = urlparse.urlunparse(parts)
    return url_with_extra_slash.replace('///', '//')

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
    LOGGER.info('Parsed location: %s %s', id, name)
    return dtos.Location(id, name, organization_id, description, spatial_location)

def parse_site_id(site):
    return site.find('Key').text

def parse_site_name(site):
    return site.find('Name').text

def parse_site_description(site):
    return site.find('SiteDescription').text

def parse_spatial_location_if_defined(site):
    latitude = site.find('SpatialLocation/Latitude')
    longitude = site.find('SpatialLocation/Longitude')
    if latitude is None or longitude is None:
        return None
    return dtos.SpatialLocation(latitude.text, longitude.text)
