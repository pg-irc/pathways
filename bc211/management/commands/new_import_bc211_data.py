import argparse
from django.core.management.base import BaseCommand
from bc211.import_counters import ImportCounters
import xml.etree.ElementTree as etree
from bc211.parser import parse_agency
from bc211.importer import save_organization
from bc211.exceptions import XmlParseException

class Command(BaseCommand):
    help = 'Import BC-211 data from XML file'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            type=argparse.FileType('r'),
                            metavar='file',
                            help='Path to XML file containing BC-211 data')

    def handle(self, *args, **options):
        counts = ImportCounters()
        file = options['file']
        nodes = etree.iterparse(file, events=('end',))
        organization_id = ''
        for _, elem in nodes:
            if elem.tag == 'Agency':
                try:
                    organization = parse_agency(elem)
                    organization_id = organization.id
                    save_organization(organization, counts)
                except XmlParseException as error:
                    error = 'Error importing the organization immediately after the one with id "%s": %s'.format(organization_id, error.__str__())
                    self.stdout.write(self.style.ERROR(status_message))
                except AttributeError as error:
                    error = 'Error importing the organization immediately after the one with id "%s": %s'.format(organization_id, error.__str__())
                    self.stdout.write(self.style.ERROR(status_message))
