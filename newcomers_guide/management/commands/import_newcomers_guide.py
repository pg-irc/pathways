from django.core.management.base import BaseCommand
from newcomers_guide.generate_fixtures import set_taxonomy_term_references_on_content
from newcomers_guide.read_data import read_topic_data, read_taxonomy_data
from newcomers_guide.parse_data import parse_topic_files, parse_taxonomy_files
from newcomers_guide.save_topics import save_topics
from bc211.import_icarol_xml.import_counters import ImportCounters


# invoke as follows:
# python manage.py import_newcomers_guide path/to/newcomers/root/directory


class Command(BaseCommand):
    help = 'Import Newcomers Guide from folder structure'

    def add_arguments(self, parser):
        parser.add_argument('path',
                            metavar='path',
                            help='path to root of Newcomers Guide folder structure')

    def handle(self, *args, **options):
        root_folder = options['path']

        self.stdout.write('Reading Newcomers Guide data from {}'.format(root_folder))

        taxonomy_data = read_taxonomy_data(root_folder)
        taxonomies = parse_taxonomy_files(taxonomy_data)

        topic_data = read_topic_data(root_folder)
        topics = parse_topic_files(topic_data)
        set_taxonomy_term_references_on_content(taxonomies, topics['taskMap'])

        counts = ImportCounters()
        save_topics(topics, counts)

# add bc or mb prefix to topic ids
