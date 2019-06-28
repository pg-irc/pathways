from django.test import TestCase
from newcomers_guide.save_topics import save_topics
from newcomers_guide.tests import helpers
from search.models import Task
from common.testhelpers.random_test_values import a_string
from bc211.import_counters import ImportCounters


class TestSavingTasks(TestCase):
    def setUp(self):
        self.counts = ImportCounters()
        self.topic_id = 'the-topic-id'
        self.english_topic_name = a_string()
        self.english_topic_description = a_string()
        self.one_topic = {
            'taskMap': {
                'the-topic-id': {
                    'id': 'the-topic-id',
                    'title': {
                        'en': self.english_topic_name,
                    },
                    'description': {
                        'en': self.english_topic_description,
                    },
                    'taxonomyTerms': [
                        {
                            'taxonomyId': 'colour',
                            'taxonomyTermId': 'blue',
                        },
                        {
                            'taxonomyId': 'size',
                            'taxonomyTermId': 'large',
                        }
                    ],
                }
            }
        }

    def test_deletes_existing_records(self):
        helpers.create_topic(a_string())
        helpers.create_topic(a_string())

        save_topics(self.one_topic, self.counts)
        self.assertEqual(Task.objects.count(), 1)

    def test_saves_topic_id(self):
        save_topics(self.one_topic, self.counts)
        records = Task.objects.all()
        self.assertEqual(records[0].id, self.topic_id)

    def test_saves_topic_title_in_english(self):
        save_topics(self.one_topic, self.counts)
        records = Task.objects.all()
        self.assertEqual(records[0].name, self.english_topic_name)

    def test_saves_topic_description_in_english(self):
        save_topics(self.one_topic, self.counts)
        records = Task.objects.all()
        self.assertEqual(records[0].description, self.english_topic_description)

    def test_saves_taxonomy_id(self):
        save_topics(self.one_topic, self.counts)
        record = Task.objects.all()[0]
        self.assertEqual(record.taxonomy_terms.all()[0].taxonomy_id, 'colour')

    def test_saves_taxonomy_term(self):
        save_topics(self.one_topic, self.counts)
        record = Task.objects.all()[0]
        self.assertEqual(record.taxonomy_terms.all()[0].name, 'blue')

    def test_saves_multiple_taxonomy_terms(self):
        save_topics(self.one_topic, self.counts)
        record = Task.objects.all()[0]
        self.assertEqual(record.taxonomy_terms.all()[0].taxonomy_id, 'colour')
        self.assertEqual(record.taxonomy_terms.all()[1].taxonomy_id, 'size')
