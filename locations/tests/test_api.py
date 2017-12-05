from rest_framework import test as rest_test
from rest_framework import status
from locations.tests.helpers import LocationBuilder
from organizations.tests.helpers import OrganizationBuilder

class LocationsApiTests(rest_test.APITestCase):
    def setUp(self):
        self.organization_id = 'the_organization_id'
        self.organization = OrganizationBuilder().with_id(self.organization_id).build()
        self.organization.save()
        self.data = {
            'id': 'the_location_id',
            'name': 'the name',
            'organization_id': self.organization_id,
            'latitude': 0.0,
            'longitude': 0.0,
            'description': 'the description'
        }

    def test_can_get_locations(self):
        LocationBuilder(self.organization).with_id('First').build().save()
        LocationBuilder(self.organization).with_id('Second').build().save()
        url = '/v1/locations/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_can_get_one_location(self):
        location = LocationBuilder(self.organization).with_description('The description').build()
        location.save()
        url = '/v1/locations/{0}/'.format(location.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['description'], 'The description')

    def test_cannot_post(self):
        url = '/v1/locations/'
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_put(self):
        location = LocationBuilder(self.organization).build()
        location.save()
        url = '/v1/locations/{0}/'.format(location.pk)
        response = self.client.put(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete(self):
        location = LocationBuilder(self.organization).build()
        location.save()
        url = '/v1/locations/{0}/'.format(location.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_can_get_locations_for_organization(self):
        LocationBuilder(self.organization).with_id('First').build().save()
        LocationBuilder(self.organization).with_id('Second').build().save()
        url = '/v1/organizations/{0}/locations/'.format(self.organization_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_can_get_one_location_for_organization(self):
        location = LocationBuilder(self.organization).with_description('The description').build()
        location.save()
        url = '/v1/organizations/{0}/locations/{1}/'.format(self.organization_id, location.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['description'], 'The description')

    def test_cannot_post_to_organization(self):
        url = '/v1/organizations/{0}/locations/'.format(self.organization_id)
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_put_to_organization(self):
        location = LocationBuilder(self.organization).build()
        location.save()
        url = '/v1/organizations/{0}/locations/{1}/'.format(self.organization_id, location.pk)
        response = self.client.put(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete_on_organization(self):
        location = LocationBuilder(self.organization).build()
        location.save()
        url = '/v1/organizations/{0}/locations/{1}/'.format(self.organization_id, location.pk)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
