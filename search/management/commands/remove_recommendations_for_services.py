from django.core.management.base import BaseCommand
from search.read_similarities import read_topics_list
from search.remove_similarities_for_services import remove_similarities_for_services


class Command(BaseCommand):
    help = ('For services for which there are no meaningful related topics, '
            'remove all related topics')

    def add_arguments(self, parser):
        parser.add_argument('service_list',
                            metavar='service_list',
                            help=('path to file containing list of ids of services to remove, '
                                  'one service id per line'))

    def handle(self, *args, **options):
        topics_list_path = options['service_list']

        service_ids = read_topics_list(topics_list_path)
        print('Removing similarities for {} services...'.format(len(service_ids)))
        remove_similarities_for_services(service_ids)
