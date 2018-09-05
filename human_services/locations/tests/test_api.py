from rest_framework import test as rest_test
from rest_framework import status
from human_services.locations.tests.helpers import LocationBuilder
from human_services.locations.models import Location, LocationAddress
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.addresses.tests.helpers import AddressBuilder
from human_services.addresses.models import Address, AddressType
from human_services.phone_numbers.tests.helpers import PhoneNumberTypeBuilder, PhoneNumberBuilder
from common.testhelpers.random_test_values import a_float


class LocationsApiTests(rest_test.APITestCase):
    def setUp(self):
        self.organization_id = 'the_organization_id'
        self.organization = OrganizationBuilder().with_id(self.organization_id).build()
        self.organization.save()
        self.data = {
            'id': 'the_location_id',
            'name': 'the name',
            'organization_id': self.organization_id,
            'description': 'the description'
        }

    def test_can_get_locations(self):
        LocationBuilder(self.organization).with_id('First').create()
        LocationBuilder(self.organization).with_id('Second').create()
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
        LocationBuilder(self.organization).with_id('First').create()
        LocationBuilder(self.organization).with_id('Second').create()
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

    def location_has_address_of_type(self, address_type_id):
        LocationBuilder(self.organization).create()
        AddressBuilder().create()
        LocationAddress(
            location=Location.objects.first(),
            address=Address.objects.first(),
            address_type=AddressType.objects.get(pk=address_type_id)
        ).save()
        url = '/v1/locations/'
        response = self.client.get(url)
        location_addresses = response.json()[0]['addresses']
        self.assertEqual(location_addresses[0]['address_type'], address_type_id)

    def test_has_physical_address(self):
        self.location_has_address_of_type('physical_address')

    def test_has_postal_address(self):
        self.location_has_address_of_type('postal_address')

    def test_has_point_values(self):
        location = LocationBuilder(self.organization).with_point(a_float(), a_float()).create()
        url = '/v1/locations/'
        response = self.client.get(url)
        self.assertEqual(response.json()[0]['latitude'], location.point.x)
        self.assertEqual(response.json()[0]['longitude'], location.point.y)

    def test_has_phone_numbers(self):
        location = LocationBuilder(self.organization).create()
        phone_number = PhoneNumberBuilder().with_location(location).create()
        url = '/v1/locations/'
        response = self.client.get(url)
        self.assertEqual(response.json()[0]['phone_numbers'][0]['phone_number_type'], phone_number.phone_number_type.id)
        self.assertEqual(response.json()[0]['phone_numbers'][0]['phone_number'], phone_number.phone_number.raw_input)

