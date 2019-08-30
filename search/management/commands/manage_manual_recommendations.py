import os
import re
from django.core.management.base import BaseCommand
from search.manual_recommendations import read_manual_similarities
from search.models import TaskServiceSimilarityScore

class Command(BaseCommand):
    help = ('Given a path to a directory, this script reads all CSV files from that '
            'directory as manual recommendations of services for topics. Format: The '
            'filenames must match corresponding topic ids, the content of the files are '
            'CSV files with a column headed "service_id" and another column headed '
            '"Include/Exclude". Values from these columns are used to create recommended '
            'service records for the given topic. All other columns are ignored. All rows '
            'where the "Include/Exclude" column contains "Exclude" are also ignored. All '
            'files not named *.csv are ignored.')

    def add_arguments(self, parser):
        parser.add_argument('path',
                            metavar='path',
                            help='path to folder containing per-topic files with recommendations')
        parser.add_argument('--reset_recommendations', action='store_true',
                            help='Remove all existing recommendations from database before importing')

    def handle(self, *args, **options):
        path = options['path']
        reset_recommendations = options['reset_recommendations']

        if reset_recommendations:
            reset_all_existing_recommendations()

        csv_filenames = get_all_csv_filenames_from_folder(path)
        for filename in csv_filenames:
            handle_recommendation_file(filename)

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

def handle_recommendation_file(filename):
    topic_id = get_topic_id_from_filename(filename)
    csv_data = read_manual_similarities(filename)
    change_records = parse_csv_data(topic_id, csv_data)
    save_changes_to_database(change_records)

def parse_csv_data(topic_id, csv_data):
    header = csv_data[0]
    rows = csv_data[1:]
    valid_rows = filter_valid_rows(rows)
    service_id_index = get_index_for_header(header, 'service_id')
    exclude_index = get_index_for_header(header, 'Include/Exclude')
    return build_change_records(topic_id, service_id_index, exclude_index, valid_rows)

def get_topic_id_from_filename(path):
    filename = os.path.basename(path)
    return filename.split('.')[0]

def get_index_for_header(header_row, expected_header):
    return header_row.index(expected_header)

def build_change_records(topic_id, service_id_index, exclude_index, rows):
    make_record = lambda line: {
        'topic_id' : topic_id,
        'service_id' : line[service_id_index],
        'exclude' : line[exclude_index],
    }
    return list(map(make_record, rows))

def filter_valid_rows(rows):
    invalid_line_pattern = "\\(\\d+ rows\\)"
    is_valid = lambda row: not re.match(invalid_line_pattern, str(row[0]))
    return filter(is_valid, rows)

def included_records(change_records):
    return list(filter(lambda record: record['exclude'] != 'Exclude', change_records))

def save_changes_to_database(change_records):
    for record in included_records(change_records):
        save_record(record)


def save_record(record):
    manual_similarity_score = 1.0
    TaskServiceSimilarityScore.objects.update_or_create(
        task_id=record['topic_id'],
        service_id=record['service_id'],
        defaults={
            'similarity_score': manual_similarity_score
        }
    )
