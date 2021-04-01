from django.test import TestCase
from search.compute_similarities import (to_topic_ids_and_descriptions,
                                         to_service_ids_and_descriptions,
                                         compute_similarities)
from human_services.services.models import Service
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from common.testhelpers.random_test_values import a_string
from newcomers_guide.parse_data import TopicBuilder


class TestTopicSimilarityScore(TestCase):
    def setUp(self):
        self.topic_id = a_string()
        self.english_topic_title = a_string()
        self.english_topic_description = a_string()
        self.data = {
            'taskMap': {
                self.topic_id: {
                    'isNewlyRecommended': False,
                    'id': self.topic_id,
                    'title': {
                        'en': self.english_topic_title,
                    },
                    'description': {
                        'en': self.english_topic_description
                    }
                }
            }
        }
        self.organization = OrganizationBuilder().create()

    def test_getting_ids_for_topic_returns_topic_id(self):
        ids, _ = to_topic_ids_and_descriptions(self.data, None)
        self.assertEqual(ids[0], self.topic_id)

    def test_converts_topic_id_to_slug(self):
        self.data['taskMap'][self.topic_id]['id'] = 'This is the id'
        ids, _ = to_topic_ids_and_descriptions(self.data, None)
        self.assertEqual(ids[0], 'this-is-the-id')

    def test_getting_description_for_topic_returns_topic_title_and_description(self):
        _, descriptions = to_topic_ids_and_descriptions(self.data, None)
        self.assertEqual(descriptions[0],
                         self.english_topic_title + ' ' + self.english_topic_description)

    def test_getting_id_for_service_returns_id(self):
        service = ServiceBuilder(self.organization).create()
        ids, _ = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertEqual(ids[0], service.id)

    def test_include_topic_for_specified_region(self):
        a_region_id = a_string()
        a_different_region_id = a_string()

        first_topic_id = a_string() + '_' + a_region_id
        second_topic_id = a_string() + '_' + a_different_region_id
        task_map = {
            'taskMap': {
                first_topic_id: {
                    'isNewlyRecommended': False,
                    'id': first_topic_id,
                    'title': {
                        'en': a_string(),
                    },
                    'description': {
                        'en': a_string()
                    }
                },
                second_topic_id: {
                    'isNewlyRecommended': False,
                    'id': second_topic_id,
                    'title': {
                        'en': a_string(),
                    },
                    'description': {
                        'en': a_string()
                    }
                }
            }
        }

        ids, _ = to_topic_ids_and_descriptions(task_map, a_region_id)

        self.assertEqual(ids, [first_topic_id])

    def test_include_service_for_specified_region(self):
        a_region_id = a_string()
        a_different_region_id = a_string()

        first_service_id = a_string() + '_' + a_region_id
        second_service_id = a_string() + '_' + a_different_region_id

        ServiceBuilder(self.organization).with_id(first_service_id).create()
        ServiceBuilder(self.organization).with_id(second_service_id).create()

        ids, _ = to_service_ids_and_descriptions(Service.objects.all(), a_region_id)
        self.assertEqual(ids, [first_service_id])

    def test_getting_description_for_service_returns_name_and_description(self):
        name = a_string()
        description = a_string()
        ServiceBuilder(self.organization).with_name(name).with_description(description).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertEqual(descriptions[0], name + ' ' + description)

    def test_computing_similarity_matrix(self):
        strings = ['aligator interloper and fumigator',
                   'likewise aligator interloper and fumigator',
                   'different lollipop candybar and icecream']

        similarity_matrix = compute_similarities(strings)

        self.assertGreater(similarity_matrix[0, 0], 0.99)
        self.assertGreater(similarity_matrix[0, 1], 0.79)
        self.assertLess(similarity_matrix[0, 2], 0.01)

    def test_similarities_ignore_case(self):
        strings = ['aligator interloper and fumigator',
                   'LIKEWISE Aligator INTERLOPER and FUmiGAtoR',
                   'different lollipop candybar and icecream']

        similarity_matrix = compute_similarities(strings)

        self.assertGreater(similarity_matrix[0, 0], 0.99)
        self.assertGreater(similarity_matrix[0, 1], 0.79)
        self.assertLess(similarity_matrix[0, 2], 0.01)

    def test_ignores_stop_words_when_computing_similarity(self):
        stop_words_from_spacy = 'already also although always among amongst amount an and another'
        strings = ['aligator interloper and fumigator',
                   'likewise aligator interloper and fumigator ' + stop_words_from_spacy,
                   'different lollipop candybar and icecream ' + stop_words_from_spacy]

        similarity_matrix = compute_similarities(strings)

        self.assertGreater(similarity_matrix[0, 0], 0.99)
        self.assertGreater(similarity_matrix[0, 1], 0.79)
        self.assertLess(similarity_matrix[0, 2], 0.01)

    def test_stop_words_are_case_insensitive(self):
        stop_words_from_spacy = 'ALREADY Also Although ALWAYS Among AMONGST Amount An AND Another'
        strings = ['aligator interloper and fumigator',
                   'likewise aligator interloper and fumigator ' + stop_words_from_spacy,
                   'different lollipop candybar and icecream ' + stop_words_from_spacy]

        similarity_matrix = compute_similarities(strings)

        self.assertGreater(similarity_matrix[0, 0], 0.99)
        self.assertGreater(similarity_matrix[0, 1], 0.79)
        self.assertLess(similarity_matrix[0, 2], 0.01)

    def test_removes_local_phone_numbers_from_description(self):
        description_with_phone_numbers = 'Call 778-123-4567 or 604-123-4567 for more information.'
        description_without_phone_numbers = ('Call  or  for more information.')
        ServiceBuilder(self.organization).with_description(description_with_phone_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(description_without_phone_numbers, descriptions[0])

    def test_removes_international_phone_numbers_from_description(self):
        description_with_phone_numbers = 'Call 1-800-123-4567 for more information.'
        description_without_phone_numbers = ('Call  for more information.')
        ServiceBuilder(self.organization).with_description(description_with_phone_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(description_without_phone_numbers, descriptions[0])

    def test_removes_phone_numbers_in_brackets_from_description(self):
        description_with_phone_numbers = 'Call 1-(800)-123-4567 or (604)-123-4567 for more information.'
        description_without_phone_numbers = ('Call  or  for more information.')
        ServiceBuilder(self.organization).with_description(description_with_phone_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(description_without_phone_numbers, descriptions[0])

    def test_removes_phone_numbers_beginning_with_plus_sign_from_description(self):
        description_with_phone_numbers = 'Call +1-800-123-4567 or +604-123-4567 for more information.'
        description_without_phone_numbers = ('Call  or  for more information.')
        ServiceBuilder(self.organization).with_description(description_with_phone_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(description_without_phone_numbers, descriptions[0])

    def test_removes_phone_numbers_beginning_with_plus_sign_and_two_numbers_from_description(self):
        description_with_phone_numbers = 'Call +49-800-123-4567 for more information.'
        description_without_phone_numbers = ('Call  for more information.')
        ServiceBuilder(self.organization).with_description(description_with_phone_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(description_without_phone_numbers, descriptions[0])

    def test_does_not_remove_numbers_that_are_not_phone_numbers(self):
        description_with_numbers = 'In 2017 the Canadian population was approximately 36,710,0000.'
        expected_description = ('In 2017 the Canadian population was approximately 36,710,0000.')
        ServiceBuilder(self.organization).with_description(description_with_numbers).create()
        _, descriptions = to_service_ids_and_descriptions(Service.objects.all(), None)
        self.assertIn(expected_description, descriptions[0])
