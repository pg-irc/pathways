from django.core.management.base import BaseCommand
from newcomers_guide.generate_fixtures import (generate_task_fixture, generate_taxonomy_fixture,
                                               set_taxonomy_term_references_on_content)
from newcomers_guide.read_data import read_task_data, read_taxonomy_data
from newcomers_guide.parse_data import parse_task_files, parse_taxonomy_files
from newcomers_guide.log_data import log_taxonomies, log_locales
from newcomers_guide.save_topics import save_topics
from bc211.import_counters import ImportCounters


# invoke as follows:
# python manage.py import_newcomers_guide path/to/newcomers/root/directory


class Command(BaseCommand):
    help = 'Import Newcomers Guide from folder structure'

    def add_arguments(self, parser):
        parser.add_argument('path',
                            metavar='path',
                            help='path to root of Newcomers Guide folder structure')
        parser.add_argument('--save_topics_to_db', action='store_true',
                            help='Save topics to the database.')

    def handle(self, *args, **options):
        root_folder = options['path']
        is_updating_db = options['save_topics_to_db']
        
        self.stdout.write('Reading Newcomers Guide data from {}'.format(root_folder))

        taxonomy_data = read_taxonomy_data(root_folder)
        taxonomies = parse_taxonomy_files(taxonomy_data)

        task_data = read_task_data(root_folder)
        tasks = parse_task_files(task_data)
        set_taxonomy_term_references_on_content(taxonomies, tasks['taskMap'])

        log_taxonomies(self.stdout, tasks['taskMap'])
        log_locales(self.stdout, tasks['taskMap'])

        with open('tasks.ts', 'w') as file:
            file.write(generate_task_fixture(tasks))

        with open('taxonomies.ts', 'w') as file:
            file.write(generate_taxonomy_fixture(taxonomies))

        if is_updating_db:
            counts = ImportCounters()
            save_topics(tasks, counts)