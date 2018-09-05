import argparse
from django.core.management.base import BaseCommand
from bc211.parser import read_records_from_file
from bc211.importer import save_records_to_database

# invoke as follows:
# python manage.py import_bc211_data path/to/bc211.xml

class Command(BaseCommand):
    help = 'Import BC-211 data from XML file'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            type=argparse.FileType('r'),
                            metavar='file',
                            help='Path to XML file containing BC-211 data')

    def handle(self, *args, **options):
        file = options['file']

        self.stdout.write(self.style.SUCCESS('Reading BC-211 data from {}'.format(file.name)))
        records = read_records_from_file(file)

        self.stdout.write(self.style.SUCCESS('Writing data to database'))
        counts = save_records_to_database(records)

        message_template = ('Successfully imported {0} organization(s), '
                            '{1} location(s), {2} service(s), '
                            '{3} taxonomy term(s), {4} address(es), {5} phone number type(s), '
                            'and {6} phone number(s)')
        status_message = message_template.format(counts.organization_count,
                                                 counts.location_count,
                                                 counts.service_count,
                                                 counts.taxonomy_term_count,
                                                 counts.address_count,
                                                 counts.phone_number_types_count,
                                                 counts.phone_numbers_count)
        self.stdout.write(self.style.SUCCESS(status_message))
