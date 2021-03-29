from django.test import TestCase
from newcomers_guide.save_topics import save_topics
from newcomers_guide.tests import helpers
from search.models import Task
from common.testhelpers.random_test_values import a_string
from bc211.import_icarol_xml.import_counters import ImportCounters


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
        self.assertEqual({r.taxonomy_id for r in record.taxonomy_terms.all()}, {'colour', 'size'})

    def test_saves_taxonomy_term(self):
        save_topics(self.one_topic, self.counts)
        record = Task.objects.all()[0]
        self.assertEqual({r.name for r in record.taxonomy_terms.all()}, {'blue', 'large'})
