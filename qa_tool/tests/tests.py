from django.utils import timezone
import pytz
from test_plus.test import TestCase
from django.core import exceptions
from common.testhelpers.database import validate_save_and_reload
from qa_tool.tests.helpers import AlgorithmBuilder, SearchLocationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from human_services.organizations.tests.helpers import OrganizationBuilder
from common.testhelpers.random_test_values import a_float, an_integer, a_string
from qa_tool.models import Score


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


class TestSearchLocationModel(TestCase):
    def test_has_name(self):
        search_location = SearchLocationBuilder().build()
        search_location_from_db = validate_save_and_reload(search_location)
        self.assertEqual(search_location_from_db.name, search_location.name)

    def test_name_field_can_be_empty(self):
        search_location = SearchLocationBuilder().with_name('').build()
        search_location_from_db = validate_save_and_reload(search_location)
        self.assertEqual(search_location_from_db.name, '')

    def test_can_create_and_retrieve_point(self):
        location = SearchLocationBuilder().with_long_lat(a_float(), a_float()).build()
        location_from_db = validate_save_and_reload(location)
        self.assertEqual(location_from_db.point, location.point)


class TestScore(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_can_create_row(self):
        value = an_integer()
        time_stamp = timezone.now()
        algorithm = AlgorithmBuilder().create()
        search_location = SearchLocationBuilder().create()
        organization = OrganizationBuilder().create()
        service = ServiceBuilder(organization).create()
        score = Score(value=value,
                      time_stamp=time_stamp,
                      algorithm=algorithm,
                      search_location=search_location,
                      service=service,
                      user=self.user
                      )
        score_from_db = validate_save_and_reload(score)

        self.assertEqual(score_from_db.value, value)
        self.assertEqual(score_from_db.algorithm, algorithm)
        self.assertEqual(score_from_db.time_stamp, time_stamp)
        self.assertEqual(score_from_db.search_location, search_location)
        self.assertEqual(score_from_db.service, service)
        self.assertEqual(score_from_db.user, self.user)
