import os
from django.core.management.base import BaseCommand
from newcomers_guide.generate_task_fixture import generate_task_fixture, generate_taxonomy_fixture
from newcomers_guide.process_files import process_all_task_files
from newcomers_guide.process_all_taxonomy_files import process_all_taxonomy_files, set_taxonomies_on_tasks


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

        task_data = self.get_task_data(root_folder)
        tasks = process_all_task_files(task_data)

        taxonomy_data = self.get_taxonomy_data(root_folder)
        taxonomies = process_all_taxonomy_files(taxonomy_data)
        set_taxonomies_on_tasks(taxonomies, tasks)

        with open('tasks.ts', 'w') as file:
            file.write(generate_task_fixture(tasks))

        with open('taxonomies.ts', 'w') as file:
            file.write(generate_taxonomy_fixture(taxonomies))

    def get_task_data(self, root_folder):
        task_data = []
        for root, _, filenames in os.walk(root_folder, topdown=False):
            for filename in filenames:
                path = os.path.join(root, filename)
                if self.is_task_file(path):
                    task_data.append([path, self.get_file_content(path)])
        return task_data

    def is_task_file(self, path):
        sep = os.sep
        return path.find(sep + 'tasks' + sep) > 0 and not self.is_taxonomy_file(path)

    def get_taxonomy_data(self, root_folder):
        taxonomy_data = []
        for root, _, filenames in os.walk(root_folder, topdown=False):
            for filename in filenames:
                path = os.path.join(root, filename)
                if self.is_taxonomy_file(path):
                    taxonomy_data.append([path, self.get_file_content(path)])
        return taxonomy_data

    def is_taxonomy_file(self, path):
        sep = os.sep
        return path.find(sep + 'taxonomy.txt') > 0

    def get_file_content(self, path):
        with open(path, 'r') as file:
            self.stdout.write('Reading {}...'.format(path))
            content = file.read()
            return content
