from rest_framework import test as rest_test
from rest_framework import status
from human_services.locations.tests.helpers import LocationBuilder
from human_services.services_at_location.tests.helpers import ServiceAtLocationBuilder
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from human_services.locations.models import ServiceAtLocation
from taxonomies.tests.helpers import TaxonomyTermBuilder


class ServicesAtLocationApiTests(rest_test.APITestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().create()
        self.service = ServiceBuilder(self.organization).create()

    def test_200_response_when_proximity_includes_plus(self):
        url = '/v1/services_at_location/?proximity=+11.1111,+222.2222'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_200_response_when_proximity_excludes_plus(self):
        url = '/v1/services_at_location/?proximity=11.1111,-222.2222'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_order_by_proximity(self):
        first_location = (LocationBuilder(self.organization)
                          .with_name('First')
                          .with_point(0, 0).create())
        second_location = (LocationBuilder(self.organization)
                           .with_name('Second')
                           .with_point(10, 10).create())
        third_location = (LocationBuilder(self.organization)
                          .with_name('Third')
                          .with_point(25, 25).create())
        fourth_location = (LocationBuilder(self.organization)
                           .with_name('Fourth')
                           .with_point(30, 30).create())

        ServiceAtLocation.objects.create(service=self.service, location=first_location)
        ServiceAtLocation.objects.create(service=self.service, location=second_location)
        ServiceAtLocation.objects.create(service=self.service, location=third_location)
        ServiceAtLocation.objects.create(service=self.service, location=fourth_location)

        at_second_location_services_url = ('/v1/services_at_location/?proximity={0},{1}'
                                           .format(second_location.point.x,
                                                   second_location.point.y))

        response = self.client.get(at_second_location_services_url)
        json = response.json()
        self.assertEqual(json[0]['location']['name'], second_location.name)
        self.assertEqual(json[1]['location']['name'], first_location.name)
        self.assertEqual(json[2]['location']['name'], third_location.name)
        self.assertEqual(json[3]['location']['name'], fourth_location.name)

    def test_can_full_text_search(self):
        service_at_locations = ServiceAtLocationBuilder().create_many()
        expected_service_at_location = service_at_locations[0]
        service_name = expected_service_at_location.service.name
        location_name = expected_service_at_location.location.name
        response = (self.client.get('/v1/services_at_location/?search={0}'.format(service_name)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], location_name)
        self.assertEqual(json[0]['service']['name'], service_name)

    def test_can_filter_by_location_id(self):
        service_at_locations = ServiceAtLocationBuilder().create_many()
        expected_service_at_location = service_at_locations[0]
        location_id = expected_service_at_location.location.id
        response = (self.client.get('/v1/locations/{0}/services_at_location/'
                                    .format(location_id)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], expected_service_at_location.location.name)
        self.assertEqual(json[0]['service']['name'], expected_service_at_location.service.name)

    def test_can_filter_by_location_id_and_service_id(self):
        service_at_locations = ServiceAtLocationBuilder().create_many()
        expected_service_at_location = service_at_locations[0]
        location_id = expected_service_at_location.location.id
        service_id = expected_service_at_location.service.id
        response = (self.client.get('/v1/locations/{0}/services/{1}/services_at_location/'
                                    .format(location_id, service_id)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], expected_service_at_location.location.name)
        self.assertEqual(json[0]['service']['name'], expected_service_at_location.service.name)

    def test_can_filter_by_service_id(self):
        service_at_locations = ServiceAtLocationBuilder().create_many()
        expected_service_at_location = service_at_locations[0]
        service_id = expected_service_at_location.service.id
        response = (self.client.get('/v1/services/{0}/services_at_location/'
                                    .format(service_id)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], expected_service_at_location.location.name)
        self.assertEqual(json[0]['service']['name'], expected_service_at_location.service.name)

    def test_can_filter_by_service_id_and_location_id(self):
        service_at_locations = ServiceAtLocationBuilder().create_many()
        expected_service_at_location = service_at_locations[0]
        service_id = expected_service_at_location.service.id
        location_id = expected_service_at_location.location.id
        response = (self.client.get('/v1/services/{0}/locations/{1}/services_at_location/'
                                    .format(service_id, location_id)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], expected_service_at_location.location.name)
        self.assertEqual(json[0]['service']['name'], expected_service_at_location.service.name)

    def test_can_page(self):
        ServiceAtLocationBuilder().create_many(count=30)
        response = self.client.get('/v1/services_at_location/?per_page=10&page=2')
        json = response.json()
        self.assertEqual(len(json), 10)

    def test_can_filter_by_taxonomy(self):
        taxonomy_terms = TaxonomyTermBuilder().create_many()
        service = ServiceBuilder(self.organization).with_taxonomy_terms(taxonomy_terms).create()
        location = LocationBuilder(self.organization).create()
        expected_service_at_location = ServiceAtLocation.objects.create(service=service,
                                                                        location=location)
        response = (self.client.get('/v1/services_at_location/?taxonomy_terms={0}.{1}'
                                    .format(taxonomy_terms[0].taxonomy_id, taxonomy_terms[0].name)))
        json = response.json()
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['location']['name'], expected_service_at_location.location.name)
        self.assertEqual(json[0]['service']['name'], expected_service_at_location.service.name)
