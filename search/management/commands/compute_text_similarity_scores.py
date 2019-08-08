from django.core.management.base import BaseCommand
from newcomers_guide.read_data import read_topic_data
from newcomers_guide.parse_data import parse_topic_files
from human_services.services.models import Service
from search.compute_similarities import (to_topic_ids_and_descriptions,
                                         to_service_ids_and_descriptions,
                                         compute_similarities)
from search.save_similarities import (save_topic_similarities,
                                      save_topic_service_similarity_scores)


class Command(BaseCommand):
    help = 'Compute text similarity scores between Newcomers\' Guide content and service provider descriptions, store them in the database'

    def add_arguments(self, parser):
        parser.add_argument('newcomers_guide_path',
                            metavar='newcomers_guide_path',
                            help='path to root of Newcomers Guide folder structure')
        parser.add_argument('--related_topics',
                            dest='related_topics',
                            type=int,
                            default=10,
                            help='for each topic, store this many related topics')
        parser.add_argument('--related_services',
                            dest='related_services',
                            type=int,
                            default=50,
                            help='for each topic, store this many related services')

    def handle(self, *args, **options):
        root_folder = options['newcomers_guide_path']
        related_topic_count = options['related_topics']
        related_service_count = options['related_services']

        print('All topic data and topic/service similarity data will be deleted and reimported')

        print('Reading topics...')
        topics = read_topic_descriptions(root_folder)
        topic_ids, topic_descriptions = to_topic_ids_and_descriptions(topics)
        print('{} topics read, reading services...'.format(len(topic_ids)))
        services = Service.objects.all()
        services = services[0:10]
        service_ids, service_descriptions = to_service_ids_and_descriptions(services)

        descriptions = topic_descriptions + service_descriptions

        print('{} services read, computing similarities...'.format(len(service_ids)))
        cosine_doc_similarities = compute_similarities(descriptions)

        print('Saving {} topic similarities...'.format(len(topic_ids)*(len(topic_ids)-1)))
        save_topic_similarities(topic_ids, cosine_doc_similarities, related_topic_count)
        print('Saving {} topic-service similarities...'.format(len(topic_ids)*len(service_ids)))
        save_topic_service_similarity_scores(topic_ids, service_ids, cosine_doc_similarities, related_service_count)


def read_topic_descriptions(root_folder):
    topic_data = read_topic_data(root_folder)
    return parse_topic_files(topic_data)
