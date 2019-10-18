from rest_framework import test as rest_test
from rest_framework import status
from qa_tool.tests.helpers import AlgorithmBuilder


class AlgorithmsTests(rest_test.APITestCase):
    def setUp(self):
        self.data = {
            'id': 'The id',
            'name': 'The name',
            'url': 'http://www.example.org',
            'notes': 'The notes'
        }

    def test_can_get_entities(self):
        AlgorithmBuilder().with_name("staging").create()
        AlgorithmBuilder().with_name("production").create()
        url = '/v1/algorithms/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_can_get_one_entity(self):
        algorithm = AlgorithmBuilder().with_notes('Algorithm notes').build()
        algorithm.save()
        url = '/v1/algorithms/{0}/'.format(algorithm.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['notes'], 'Algorithm notes')

    def test_cannot_post(self):
        url = '/v1/algorithms/'
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_put(self):
        algorithm = AlgorithmBuilder().build()
        algorithm.save()
        url = '/v1/algorithms/{0}/'.format(algorithm.pk)
        response = self.client.put(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete(self):
        algorithm = AlgorithmBuilder().build()
        algorithm.save()
        url = '/v1/algorithms/{0}/'.format(algorithm.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
