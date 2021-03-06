import csv
import os
import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from bc211.import_open_referral_csv.headers_match_expected_format import (
    headers_match_expected_format)
from bc211.import_open_referral_csv.exceptions import InvalidFileCsvImportException
from bc211.import_open_referral_csv import parser
from bc211.import_open_referral_csv.exceptions import CsvParseException
from human_services.phone_at_location.models import PhoneNumberType, PhoneAtLocation


LOGGER = logging.getLogger(__name__)


def import_phones_file(root_folder, collector, counters):
    filename = 'phones.csv'
    path = os.path.join(root_folder, filename)
    read_file(path, collector, counters)


def read_file(path, collector, counters):
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        headers = reader.__next__()
        if not headers_match_expected_format(headers, expected_headers):
            raise InvalidFileCsvImportException(
                'The headers in "{0}": does not match open referral standards.'.format(path)
            )
        read_and_import_rows(reader, collector, counters)


expected_headers = ['id', 'location_id', 'service_id', 'organization_id', 'contact_id',
                    'service_at_location_id', 'number', 'extension', 'type', 'language',
                    'description', 'department']


def read_and_import_rows(reader, collector, counters):
    for row in reader:
        if not row:
            continue
        import_phone(row, collector, counters)


def import_phone(row, collector, counters):
    try:
        location_id = parser.parse_required_field_with_double_escaped_html('location_id', row[1])
        create_phone_number_type_active_record(row)
        counters.count_phone_number_types()
        if collector.has_inactive_location_id(location_id):
            return
        phone_at_location_active_record = build_phone_at_location_active_record(row)
        phone_at_location_active_record.save()
        counters.count_phone_at_location()
    except ValidationError as error:
        LOGGER.warning('%s', error.__str__())
    except IntegrityError as error:
        LOGGER.warning('%s', error.__str__())
        # Phone types are missing in many csv rows
    except CsvParseException as error:
        pass


def create_phone_number_type_active_record(row):
    active_record = PhoneNumberType()
    active_record.id = parser.parse_required_field_with_double_escaped_html('phone_type', row[8])
    active_record.save()


def build_phone_at_location_active_record(row):
    active_record = PhoneAtLocation()
    active_record.location_id = parser.parse_required_field_with_double_escaped_html(
        'location_id',
        row[1]
    )
    active_record.phone_number = parser.parse_phone_number(row[6])
    phone_type = parser.parse_required_field_with_double_escaped_html('phone_type', row[8])
    active_record.phone_number_type = PhoneNumberType.objects.get(pk=phone_type)
    return active_record
