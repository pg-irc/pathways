import csv
import os
import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from bc211.open_referral_csv_import.headers_match_expected_format import (
    headers_match_expected_format)
from bc211.open_referral_csv_import.exceptions import InvalidFileCsvImportException
from bc211.open_referral_csv_import import parser
from human_services.services.models import Service
from taxonomies.models import TaxonomyTerm

LOGGER = logging.getLogger(__name__)


def import_services_taxonomy_file(root_folder, collector):
    filename = 'services_taxonomy.csv'
    path = os.path.join(root_folder, filename)
    read_file(path, collector)


def read_file(path, collector):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        headers = reader.__next__()
        if not headers_match_expected_format(headers, expected_headers):
            raise InvalidFileCsvImportException(
                'The headers in "{0}": does not match open referral standards.'.format(path)
            )
        read_and_import_rows(reader, collector)


expected_headers = ['id', 'service_id', 'taxonomy_id', 'taxonomy_detail']


def read_and_import_rows(reader, collector):
    service = None
    for row in reader:
        if not row:
            continue
        service_id = parser.parse_required_field_with_double_escaped_html('service_id', row[1])
        if collector.has_inactive_service_id(service_id):
            continue
        service = get_service_active_record_or_raise(service_id)
        import_service_taxonomy(row, service)


def import_service_taxonomy(row, service):
    try:
        taxonomy_id = parser.parse_required_field_with_double_escaped_html('taxonomy_id', row[2])
        taxonomy_term = get_taxonomy_term_active_record_or_raise(taxonomy_id)
        service.taxonomy_terms.add(taxonomy_term)
    except ValidationError as error:
        LOGGER.warning('%s', error.__str__())
    except ObjectDoesNotExist:
        pass


def build_service_taxonomy_active_record(service_id, taxonomy_term):
    service_active_record = get_service_active_record_or_raise(service_id)
    service_active_record.taxonomy_terms.add(taxonomy_term)
    return service_active_record


def get_service_active_record_or_raise(service_id):
    try:
        return Service.objects.get(pk=service_id)
    except ObjectDoesNotExist as error:
        LOGGER.warning('Service record with id "%s" does not exist. %s', service_id, error)
        raise


def get_taxonomy_term_active_record_or_raise(taxonomy_id):
    try:
        return TaxonomyTerm.objects.get(taxonomy_id=taxonomy_id)
    except ObjectDoesNotExist:
        LOGGER.warning('Taxonomy record with id "%s" does not exist.', taxonomy_id)
        raise
