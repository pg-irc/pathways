import logging
import csv
from bc211 import dtos
from django.utils import translation
from django.contrib.gis.geos import Point
from human_services.locations.models import Location, ServiceAtLocation, LocationAddress
from human_services.organizations.models import Organization
from human_services.services.models import Service
from human_services.addresses.models import Address, AddressType
from human_services.phone_at_location.models import PhoneNumberType, PhoneAtLocation
from taxonomies.models import TaxonomyTerm
from bc211.exceptions import XmlParseException

LOGGER = logging.getLogger(__name__)


def parse_csv(csv_path):
    with open(csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        city_to_latlong = {rows[0]: Point(float(rows[1]), float(rows[2])) for rows in csv_reader}
        return city_to_latlong


def save_records_to_database(organizations, counters):
    for organization in handle_parser_errors(organizations):
        save_organization(organization, {}, counters)


def save_organization(organization, city_latlong_map, counters):
    if is_inactive(organization):
        return
    translation.activate('en')
    active_record = build_organization_active_record(organization)
    active_record.save()
    counters.count_organization()
    LOGGER.debug('Organization "%s" "%s"', organization.id, organization.name)
    save_locations(organization.locations, city_latlong_map, counters)


def handle_parser_errors(generator):
    organization_id = ''
    while True:
        try:
            organization = next(generator)
            organization_id = organization.id
            yield organization
        except StopIteration:
            return
        except XmlParseException as error:
            LOGGER.error('Error importing the organization immediately after the one with id "%s": %s',
                         organization_id, error.__str__())


def build_organization_active_record(record):
    active_record = Organization()
    active_record.id = record.id
    active_record.name = record.name
    active_record.description = record.description
    active_record.website = record.website
    active_record.email = record.email
    return active_record


def save_locations(locations, city_latlong_map, counters):
    for location in locations:
        if is_inactive(location):
            continue
        valid_location = validate_latlong_on_location(location, city_latlong_map)
        active_record = build_location_active_record(valid_location)
        active_record.save()
        counters.count_location()
        LOGGER.debug('Location "%s" "%s"', location.id, location.name)
        if location.services:
            save_services(location.services, counters)
        if location.physical_address:
            create_address_for_location(active_record, location.physical_address, counters)
        if location.postal_address:
            create_address_for_location(active_record, location.postal_address, counters)
        if location.phone_numbers:
            create_phone_numbers_for_location(active_record, location.phone_numbers, counters)


def validate_latlong_on_location(location_dto, city_latlong_map):
    if location_dto.spatial_location is not None:
        return location_dto
    if location_dto.physical_address is None:
        LOGGER.warning('Location with id "%s" does not have LatLong or physical address',
                       location_dto.id)
        return location_dto
    if location_dto.physical_address.city in city_latlong_map:
        replacement_point = city_latlong_map[location_dto.physical_address.city]
        replacement_spatial_location = dtos.SpatialLocation(
            latitude=replacement_point.y,
            longitude=replacement_point.x
        )
        location_dto.spatial_location = replacement_spatial_location
        return location_dto
    LOGGER.warning('Location with id "%s" does not have city to fall back on for LatLong info',
                   location_dto.id)
    return location_dto


def is_inactive(record):
    # This is BC211's convention for marking records as inactive
    return record.description and record.description.strip().startswith('DEL')


def build_location_active_record(record):
    active_record = Location()
    active_record.id = record.id
    active_record.name = record.name
    active_record.organization_id = record.organization_id
    has_location = record.spatial_location is not None
    if has_location:
        active_record.point = Point(record.spatial_location.longitude, record.spatial_location.latitude)
    active_record.description = record.description
    return active_record


def build_service_active_record(record):
    active_record = Service()
    active_record.id = record.id
    active_record.name = record.name
    active_record.organization_id = record.organization_id
    active_record.description = record.description
    active_record.last_verified_date = record.last_verified_date
    return active_record


def build_service_at_location_active_record(record):
    active_record = ServiceAtLocation()
    active_record.service_id = record.id
    active_record.location_id = record.site_id
    return active_record


def save_services(services, counters):
    for service in services:
        if is_inactive(service) or service_already_exists(service):
            continue
        active_record = build_service_active_record(service)
        active_record.save()
        counters.count_service()
        LOGGER.debug('Service "%s" "%s"', service.id, service.name)
        save_service_at_location(service)
        save_service_taxonomy_terms(service.taxonomy_terms, active_record, counters)


def service_already_exists(service):
    return Service.objects.filter(pk=service.id).exists()


def save_service_at_location(service):
    active_record = build_service_at_location_active_record(service)
    active_record.save()
    LOGGER.debug('Service at location: %s %s', service.id, service.site_id)


def save_service_taxonomy_terms(taxonomy_terms, service_active_record, counters):
    for taxonomy_term in taxonomy_terms:
        taxonomy_term_active_record = create_taxonomy_term_active_record(
            taxonomy_term,
            counters
        )
        service_active_record.taxonomy_terms.add(taxonomy_term_active_record)
        LOGGER.debug('Imported service taxonomy term')
    service_active_record.save()


def create_taxonomy_term_active_record(record, counters):
    taxonomy_term_active_record, created = TaxonomyTerm.objects.get_or_create(
        taxonomy_id=record.taxonomy_id,
        name=record.name
    )
    if created:
        counters.count_taxonomy_term()
        LOGGER.debug('Taxonomy term "%s" "%s"', record.taxonomy_id, record.name)
    return taxonomy_term_active_record


def create_address_for_location(location, address_dto, counters):
    address = create_address(address_dto, counters)
    address_type = AddressType.objects.get(pk=address_dto.address_type_id)
    create_location_address(
        location,
        address,
        address_type
    )


def create_address(address_dto, counters):
    active_record, created = Address.objects.get_or_create(
        address=address_dto.address_lines,
        city=address_dto.city,
        country=address_dto.country,
        state_province=address_dto.state_province,
        postal_code=address_dto.postal_code,
        attention=None
    )
    if created:
        counters.count_address()
        LOGGER.debug('Address: %s %s', active_record.id, active_record.address)
    return active_record


def create_location_address(location, address, address_type):
    active_record = LocationAddress(address=address, location=location,
                                    address_type=address_type).save()
    LOGGER.debug('Location address')
    return active_record


def create_phone_numbers_for_location(location, phone_number_dtos, counters):
    for dto in phone_number_dtos:
        phone_number_type, created = PhoneNumberType.objects.get_or_create(
            id=dto.phone_number_type_id
        )
        if created:
            counters.count_phone_number_types()
            LOGGER.debug('PhoneNumberType: "%s"', phone_number_type.id)
        number = PhoneAtLocation.objects.create(
            location=location,
            phone_number_type=phone_number_type,
            phone_number=dto.phone_number
        )
        counters.count_phone_at_location()
        LOGGER.debug('PhoneNumber: "%s" "%s"', number.id, number.phone_number)
