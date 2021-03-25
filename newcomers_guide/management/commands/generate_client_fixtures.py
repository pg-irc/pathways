from django.core.management.base import BaseCommand
from newcomers_guide.generate_fixtures import (generate_topic_fixture, generate_taxonomy_fixture,
                                               set_taxonomy_term_references_on_content)
from newcomers_guide.read_data import read_topic_data, read_taxonomy_data
from newcomers_guide.parse_data import parse_topic_files, parse_taxonomy_files
from newcomers_guide.log_data import log_taxonomies, log_locales


# invoke as follows:
# python manage.py generate_client_fixtures path/to/newcomers/root/directory


class Command(BaseCommand):
    help = 'Generate fixture files containing newcomers guide data. These are used to build the client.'

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

        log_taxonomies(self.stdout, topics['taskMap'])
        log_locales(self.stdout, topics['taskMap'])

        with open('tasks.ts', 'w') as file:
            file.write(generate_topic_fixture(topics))

        with open('taxonomies.ts', 'w') as file:
            file.write(generate_taxonomy_fixture(taxonomies))
