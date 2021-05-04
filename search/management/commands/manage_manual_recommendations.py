import os
import re
import logging
from django.core.management.base import BaseCommand
from django.core import exceptions
from search.read_csv_data_from_file import read_csv_data_from_file
from search.models import TaskServiceSimilarityScore
from human_services.services.models import Service

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ('Given a path to a directory, this script reads all CSV files from that '
            'directory as manual recommendations of services for topics. Format: The '
            'filenames must match corresponding topic ids, the content of the files are '
            'CSV files with a column headed "service_id" and another column headed '
            '"Include/Exclude". Values from these columns are used to create recommended '
            'service records for the given topic. All such records will have similarity '
            'scores of 1.0. All other columns are ignored. If the "Include/Exclude" column '
            'contains "Exclude", then records are not created, instead any existing '
            'recommendation record for the given topic and service is removed, so that '
            'the given service will not be recommended for the given topic.')

    def add_arguments(self, parser):
        parser.add_argument('path',
                            metavar='path',
                            help='path to folder containing per-topic files with recommendations')
        parser.add_argument('--reset_recommendations', action='store_true',
                            help='Remove all existing recommendations from database before importing')
        parser.add_argument('region', metavar='region', help='Add regional postfix to service and topic primary keys')

    def handle(self, *args, **options):
        path = options['path']
        reset_recommendations = options['reset_recommendations']
        region = options['region']

        if reset_recommendations:
            reset_all_existing_recommendations()

        csv_filenames = get_all_csv_filenames_from_folder(path)
        for filename in csv_filenames:
            try:
                handle_recommendation_file(filename, region)
            except exceptions.ValidationError as error:
                self.print_error(filename, error)
            except ValueError as error:
                self.print_error(filename, error)

    def print_error(self, filename, error):
        error = '{filename}: {error_message}'.format(
            filename=filename, error_message=error.__str__())
        self.stdout.write(self.style.ERROR(error))


def reset_all_existing_recommendations():
    TaskServiceSimilarityScore.objects.all().delete()


def get_all_csv_filenames_from_folder(path):
    result = []
    directory = os.fsencode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".csv"):
            result.append(path + filename)
    return result


def handle_recommendation_file(filename, region):
    topic_id = get_topic_id_from_filename(filename)
    csv_data = read_csv_data_from_file(filename)
    change_records = parse_csv_data(topic_id, region, csv_data)
    save_changes_to_database(change_records)


def parse_csv_data(topic_id, region, csv_data):
    header = csv_data[0]
    rows = csv_data[1:]
    valid_rows = remove_row_count_line(rows)
    service_id_index = get_index_for_header(header, 'service_id')
    exclude_index = get_index_for_header(header, 'Include/Exclude')
    return build_change_records(topic_id, service_id_index, exclude_index, region, valid_rows)


def get_topic_id_from_filename(path):
    filename = os.path.basename(path)
    return filename.split('.')[0]


def get_index_for_header(header_row, expected_header):
    return header_row.index(expected_header)


def build_change_records(topic_id, service_id_index, exclude_index, region, rows):
    def add_region(region, the_id):
        if region:
            return f'{the_id}_{region}'
        return the_id

    def make_record(line): return {
        'topic_id': add_region(region, topic_id),
        'service_id': add_region(region, line[service_id_index]),
        'exclude': line[exclude_index],
    }
    return list(map(make_record, rows))


def remove_row_count_line(rows):
    invalid_line_pattern = "\\(\\d+ rows\\)"
    def is_valid(row): return not re.match(invalid_line_pattern, str(row[0]))
    return filter(is_valid, rows)


def save_changes_to_database(change_records):
    valid_records = validate_records(change_records)
    for record in filter_excluded_records(valid_records):
        remove_record(record)
    for record in filter_included_records(valid_records):
        if validate_service_id(record):
            save_record(record)


def validate_records(change_records):
    for record in change_records:
        exclude = record['exclude']
        if exclude != 'Exclude' and exclude != 'Include':
            raise exceptions.ValidationError(exclude + ': Invalid value in the Include/Exclude column')
    return change_records

def validate_service_id(record):
    try:
        Service.objects.get(id=record['service_id'])
    except:
        LOGGER.warning('%s: Invalid service id', record['service_id'])
        return False
    return True

def filter_included_records(change_records):
    return filter(lambda record: record['exclude'] != 'Exclude', change_records)


def filter_excluded_records(change_records):
    return filter(lambda record: record['exclude'] == 'Exclude', change_records)


def remove_record(record):
    (TaskServiceSimilarityScore.objects.
     filter(task_id__exact=record['topic_id']).
     filter(service_id__exact=record['service_id']).
     delete())


def save_record(record):
    manual_similarity_score = 1.0
    TaskServiceSimilarityScore.objects.update_or_create(
        task_id=record['topic_id'],
        service_id=record['service_id'],
        defaults={
            'similarity_score': manual_similarity_score
        }
    )
