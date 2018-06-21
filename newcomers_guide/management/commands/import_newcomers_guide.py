import os
from django.core.management.base import BaseCommand
from newcomers_guide import generate_task_fixture

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

        data = []
        for root, _, filenames in os.walk(root_folder, topdown=False):
            for filename in filenames:
                path = os.path.join(root, filename)
                with open(path, 'r') as file:
                    self.stdout.write('Reading {}...'.format(path))
                    content = file.read()
                    data.append([path, content])

        with open('tasks.ts', 'w') as file:
            fixture = generate_task_fixture.generate_task_fixture(data)
            file.write(fixture)
