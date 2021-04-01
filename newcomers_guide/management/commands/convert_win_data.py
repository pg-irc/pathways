import os
from django.core.management.base import BaseCommand
from bc211.import_icarol_xml.import_counters import ImportCounters
from newcomers_guide.split_win_file import parse_file

# invoke as follows:
# ./manage.py convert_win_data path/to/input/file.txt path/for/output

# Expected input file format:

# 1 CHAPTER 1 - Things to do right away
# 1.23 Topic: The name of the topic
# Tags: first:tag second:tag
# Content of the topic bla bla bla
# Content of the topic bla bla bla
# Content of the topic bla bla bla
# Content of the topic bla bla bla
# Content of the topic bla bla bla
# 1.23 Topic: The name of the next topic
# etc...


class Command(BaseCommand):
    help = 'Import Winnipeg Introduction for Newcomers (WIN) from single text file'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            metavar='file',
                            help='path to the file containing the WIN content')
        parser.add_argument('path',
                            metavar='path',
                            help='path where the output will be written')

    def handle(self, *args, **options):
        inputfile = options['file']
        path = options['path']
        self.stdout.write(f'reading {inputfile}')
        data = parse_file(self.stdout, inputfile)
        self.stdout.write(f'parsed {len(data.topics)} topics')
        for topic in data.topics:
            os.makedirs(topic.file_path(path), exist_ok=True)
            locale = 'en'
            file_name = topic.file_name(path, locale)
            self.stdout.write(f'writing data to {file_name}')
            with open(file_name, 'w') as fp:
                fp.write(topic.text)
            with open(topic.taxonomy_file_name(path), 'w') as fp:
                fp.write(topic.tags_for_writing())
