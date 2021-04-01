import argparse
from django.core.management.base import BaseCommand
from bc211.convert_icarol_csv.parser import parse
from bc211.convert_icarol_csv.csv_file_sink import CsvFileSink

# invoke as follows:
# python manage.py import_bc211_csv_data path/to/bc211.csv


class Command(BaseCommand):
    help = 'Convert data in BC211 CSV export format to openReferral standard CSV files'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            type=argparse.FileType('r', encoding='ISO-8859-1'),
                            metavar='file',
                            help='Path to CSV file containing BC-211 data')
        parser.add_argument('path', metavar='path', help='Path to output folder, which must already exist')
        parser.add_argument('region', metavar='region', help='region id, such as bc or mb, added to all ids to avoid conflicts')
        parser.add_argument('--vocabulary', default=None, help='the vocabulary id for taxonomy terms, defaults to BC211 or AIRS')

    def handle(self, *args, **options):
        parse(CsvFileSink(options['path']),
              options['file'],
              options['region'],
              options['vocabulary']
            )
