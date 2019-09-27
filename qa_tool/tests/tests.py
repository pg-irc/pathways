from django.test import TestCase
from django.core import exceptions
from common.testhelpers.database import validate_save_and_reload
from qa_tool.tests.helpers import AlgorithmBuilder


class TestAlgorithmModel(TestCase):

    def test_has_name(self):
        algorithm = AlgorithmBuilder().build()
        algorithm_from_db = validate_save_and_reload(algorithm)
        self.assertEqual(algorithm_from_db.name, algorithm.name)

    def test_name_field_cannot_be_empty(self):
        name = ''
        algorithm = AlgorithmBuilder().with_name(name).build()
        with self.assertRaises(exceptions.ValidationError):
            algorithm.full_clean()

    def test_has_url(self):
        algorithm = AlgorithmBuilder().build()
        algorithm_from_db = validate_save_and_reload(algorithm)
        self.assertEqual(algorithm_from_db.url, algorithm.url)

    def test_url_field_cannot_be_empty(self):
        algorithm_url = ''
        algorithm = AlgorithmBuilder().with_url(algorithm_url).build()
        with self.assertRaises(exceptions.ValidationError):
            algorithm.full_clean()

    def test_has_notes(self):
        algorithm = AlgorithmBuilder().build()
        algorithm_from_db = validate_save_and_reload(algorithm)
        self.assertEqual(algorithm_from_db.notes, algorithm.notes)

    def test_notes_field_can_be_empty(self):
        algorithm = AlgorithmBuilder().with_notes('').build()
        algorithm_from_db = validate_save_and_reload(algorithm)
        self.assertEqual(algorithm_from_db.notes, '')
