import argparse
from django.core.management.base import BaseCommand
from newcomers_guide.read_data import read_topic_data
from newcomers_guide.parse_data import parse_topic_files
from human_services.services.models import Service
from search.compute_similarities import (to_topic_ids_and_descriptions,
                                         to_service_ids_and_descriptions,
                                         compute_similarities_by_tf_idf)
from search.save_similarities import (save_topic_similarities,
                                      save_topic_service_similarity_scores)


class Command(BaseCommand):
    help = 'Compute text similarity scores between Newcomers\' Guide content and service provider descriptions, store them in the database'

    def add_arguments(self, parser):
        parser.add_argument('newcomers_guide_path',
                            metavar='newcomers_guide_path',
                            help='path to root of Newcomers Guide folder structure')
        parser.add_argument('--region',
                            metavar='region',
                            help='Help')
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
        parser.add_argument('--save_intermediate_results',
                            dest='results_to_save',
                            type=int,
                            default=0,
                            help=('Save NLP word-scores to a CSV file for all the words ' +
                                  'in this many documents (i.e. topics and services), default is none. ' +
                                  'This data is useful to know what words to add to the stop words.'))
        parser.add_argument('--results_file',
                            dest='results_file',
                            nargs='?',
                            type=argparse.FileType('w'),
                            help='path to file for saving word-scores, required if --save_intermediate_results is given')

    def handle(self, *args, **options):
        root_folder = options['newcomers_guide_path']
        region = options['region']
        related_topic_count = options['related_topics']
        related_service_count = options['related_services']
        results_to_save = options['results_to_save']
        results_file = options['results_file']

        print('All topic data and topic/service similarity data will be deleted and reimported')

        print('Reading topics...')
        topics = read_topic_descriptions(root_folder)
        topic_ids, topic_descriptions = to_topic_ids_and_descriptions(topics, region)
        print('{} topics read, reading services...'.format(len(topic_ids)))

        if related_service_count > 0:
            services = Service.objects.all()
            service_ids, service_descriptions = to_service_ids_and_descriptions(services, region)
        else:
            service_ids = []
            service_descriptions = []

        descriptions = topic_descriptions + service_descriptions

        print('{} services read, computing similarities...'.format(len(service_ids)))
        cosine_doc_similarities = compute_similarities_by_tf_idf(descriptions,
                                                                 topic_ids,
                                                                 service_ids,
                                                                 results_to_save,
                                                                 results_file)

        print('Saving {} topic similarities...'.format(len(topic_ids)*(len(topic_ids)-1)))
        save_topic_similarities(topic_ids, cosine_doc_similarities, related_topic_count)
        print('Saving {} topic-service similarities...'.format(len(topic_ids)*len(service_ids)))
        save_topic_service_similarity_scores(topic_ids, service_ids, cosine_doc_similarities, related_service_count)


def read_topic_descriptions(root_folder):
    topic_data = read_topic_data(root_folder)
    return parse_topic_files(topic_data)
