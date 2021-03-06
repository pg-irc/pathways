import csv
import os
import logging
from django.core.exceptions import ValidationError
from bc211.import_open_referral_csv.headers_match_expected_format import (
    headers_match_expected_format)
from bc211.import_open_referral_csv.exceptions import InvalidFileCsvImportException
from bc211.import_open_referral_csv import parser
from taxonomies.models import TaxonomyTerm

LOGGER = logging.getLogger(__name__)


def import_taxonomy_file(root_folder, counters):
    filename = 'taxonomy.csv'
    path = os.path.join(root_folder, filename)
    read_file(path, counters)


def read_file(path, counters):
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        headers = reader.__next__()
        if not headers_match_expected_format(headers, expected_headers):
            raise InvalidFileCsvImportException(
                'The headers in "{0}": does not match open referral standards.'.format(path)
            )
        read_and_import_rows(reader, counters)


expected_headers = ['id', 'name', 'parent_id', 'parent_name', 'vocabulary']


def read_and_import_rows(reader, counters):
    for row in reader:
        if not row:
            continue
        existing = get_existing_taxonomy_or_none(row)
        if not existing:
            import_taxonomy(row, counters)


def get_existing_taxonomy_or_none(row):
    result = TaxonomyTerm.objects.filter(id=row[0], name=row[1], taxonomy_id=row[4]).all()
    return result[0] if result else None


def import_taxonomy(row, counters):
    try:
        active_record = build_taxonomy_active_record(row)
        active_record.save()
        counters.count_taxonomy_term()
    except ValidationError as error:
        LOGGER.warning('%s', error.__str__())


def build_taxonomy_active_record(row):
    active_record = TaxonomyTerm()
    active_record.id = row[0]
    active_record.name = row[1]
    active_record.taxonomy_id = row[4]
    return active_record
