import csv
import os
import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from human_services.addresses.models import Address, AddressType
from human_services.locations.models import LocationAddress, Location
from bc211.open_referral_csv_import import parser
from bc211.open_referral_csv_import.headers_match_expected_format import (
    headers_match_expected_format)
from bc211.open_referral_csv_import.exceptions import InvalidFileCsvImportException
from bc211.open_referral_csv_import.exceptions import CsvParseException

LOGGER = logging.getLogger(__name__)


def import_addresses_file(root_folder, collector, counters):
    filename = 'addresses.csv'
    path = os.path.join(root_folder, filename)
    read_file(path, collector, counters)


def read_file(path, collector, counters):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        headers = reader.__next__()
        if not headers_match_expected_format(headers, expected_headers):
            raise InvalidFileCsvImportException(
                'The headers in "{0}": does not match open referral standards.'.format(path)
            )
        read_and_import_rows(reader, collector, counters)


expected_headers = ['id', 'type', 'location_id', 'attention', 'address_1', 'address_2', 'address_3',
                'address_4', 'city', 'region', 'state_province', 'postal_code', 'country']


def read_and_import_rows(reader, collector, counters):
    for row in reader:
        if not row:
            continue
        address_active_record = import_address(row, counters)
        import_location_address(row, address_active_record, collector, counters)


def import_address(row, counters):
    try:
        address_active_record = build_address_active_record(row)
        address_active_record.save()
        counters.count_address()
        return address_active_record
    except ValidationError as error:
        LOGGER.warning('%s', error.__str__())
    except CsvParseException as error:
        LOGGER.warning('%s', error.__str__())


def build_address_active_record(row):
    active_record = Address()
    active_record.id = parser.parse_required_field_with_double_escaped_html('address_id', row[0])
    active_record.attention = parser.parse_optional_field_with_double_escaped_html(row[3])
    addresses = [row[4], row[5], row[6], row[7]]
    active_record.address = parser.parse_addresses(addresses)
    active_record.city = parser.parse_optional_field_with_double_escaped_html(row[8])
    active_record.state_province = parser.parse_optional_field_with_double_escaped_html(row[10])
    active_record.postal_code = parser.parse_optional_field_with_double_escaped_html(row[11])
    active_record.country = parser.parse_country(row[12])
    return active_record


def import_location_address(row, address, collector, counters):
    location_id = parser.parse_required_field_with_double_escaped_html('location_id', row[2])
    if collector.has_inactive_location_id(location_id):
        return
    create_location_address_active_record(row, address, location_id, counters)


def create_location_address_active_record(row, address, location_id, counters):
    try:
        address_type = parser.parse_required_field_with_double_escaped_html('address_type', row[1])
        location_active_record = get_active_record_or_raise(location_id, Location)
        address_type_active_record = get_active_record_or_raise(address_type, AddressType)
        LocationAddress(
                address=address,
                location=location_active_record,
                address_type=address_type_active_record
        ).save()
        counters.count_location_address()
    except ValidationError:
        LOGGER.warning(
            'ValidationError in row with location id "%s" and address "%s"', location_id, address
        )


def get_active_record_or_raise(active_record_id, model):
    try:
        return model.objects.get(pk=active_record_id)
    except ObjectDoesNotExist as error:
        LOGGER.warning('Record with id %s does not exist. %s', active_record_id, error)
