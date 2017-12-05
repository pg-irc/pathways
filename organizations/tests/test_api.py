from rest_framework import test as rest_test
from rest_framework import status
from organizations.tests.helpers import OrganizationBuilder


class OrganizationsApiTests(rest_test.APITestCase):
    def setUp(self):
        self.data = {
            'id': 'The id',
            'website': 'http://www.example.org',
            'email': 'someone@www.example.org',
            'name': 'The name',
            'description': 'The description'
        }

    def test_can_get_entities(self):
        OrganizationBuilder().with_id('First').build().save()
        OrganizationBuilder().with_id('Second').build().save()
        url = '/v1/organizations/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_can_get_one_entity(self):
        organization = OrganizationBuilder().with_description('Organization description').build()
        organization.save()
        url = '/v1/organizations/{0}/'.format(organization.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['description'], 'Organization description')

    def test_cannot_post(self):
        url = '/v1/organizations/'
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_put(self):
        organization = OrganizationBuilder().build()
        organization.save()
        url = '/v1/organizations/{0}/'.format(organization.pk)
        response = self.client.put(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete(self):
        organization = OrganizationBuilder().build()
        organization.save()
        url = '/v1/organizations/{0}/'.format(organization.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
