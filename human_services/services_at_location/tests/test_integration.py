import subprocess
import json
import os
from human_services.locations.tests.helpers import LocationBuilder
from human_services.services_at_location.tests.helpers import (set_location_for_service,
                                                               set_service_similarity_score)
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from newcomers_guide.tests.helpers import create_topic
from common.testhelpers.random_test_values import a_string, a_latitude, a_longitude
from django.test.testcases import LiveServerTestCase


class ServicesAtLocationIntegrationTests(LiveServerTestCase):
    def test_get_service_from_server(self):
        if not os.path.isfile('./run_integration_tests'):
            print('Integration test not run, run ./utility/enable_integration_tests.sh to enable')
            return

        organization = OrganizationBuilder().create()
        service = ServiceBuilder(organization).create()
        longitude = a_longitude()
        latitude = a_latitude()
        location = LocationBuilder(organization).with_long_lat(longitude, latitude).create()
        set_location_for_service(service.id, location.id)
        topic_id = a_string()
        create_topic(topic_id)
        set_service_similarity_score(topic_id, service.id, 0.9)

        response = self.make_service_request(topic_id, (longitude, latitude))

        try:
            parsed_response = json.loads(response)
            self.assertEqual(parsed_response['results'][0]['service']['id'], service.id)
        except json.decoder.JSONDecodeError:
            print('Error parsing JSON')
            print(response)

    def make_service_request(self, topic_id, a_point):
        host = self.live_server_url
        working_directory = '../pathways-frontend/'
        output = subprocess.run(args=[('yarn run ts-node src/api/integration_test.ts' +
                                       ' --host ' + host +
                                       ' --topic ' + topic_id +
                                       ' --longitude ' + str(a_point[0]) +
                                       ' --latitude ' + str(a_point[1]))],
                                cwd=working_directory,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True,
                               )
        response = output.stdout.decode('utf-8')
        start_index = response.find('START_OF_RESPONSE') + len('START_OF_RESPONSE')
        end_index = response.find('END_OF_RESPONSE')

        return response[start_index:end_index].strip()

    def test_only_return_services_related_to_given_topic(self):
        if not os.path.isfile('./run_integration_tests'):
            return

        organization = OrganizationBuilder().create()
        related_service = ServiceBuilder(organization).create()
        unrelated_service = ServiceBuilder(organization).create()

        longitude = a_longitude()
        latitude = a_latitude()
        location = LocationBuilder(organization).with_long_lat(longitude, latitude).create()
        set_location_for_service(related_service.id, location.id)
        set_location_for_service(unrelated_service.id, location.id)

        topic_id = a_string()
        create_topic(topic_id)
        set_service_similarity_score(topic_id, related_service.id, 0.9)
        # no service similarity score is set for unrelated_service

        response = self.make_service_request(topic_id, (longitude, latitude))

        try:
            parsed_response = json.loads(response)
            self.assertEqual(len(parsed_response['results']), 1)
            self.assertEqual(parsed_response['results'][0]['service']['id'], related_service.id)
        except json.decoder.JSONDecodeError:
            print('Error parsing JSON')
            print(response)

    def test_return_services_ordered_by_distance_to_proximity_point(self):
        if not os.path.isfile('./run_integration_tests'):
            return

        a_point = (12.3, 45.6)
        a_nearby_point = (12.3001, 45.6001)
        a_far_away_point = (12.301, 45.601)
        a_further_away_point = (12.31, 45.61)

        organization = OrganizationBuilder().create()

        a_nearby_service = ServiceBuilder(organization).create()
        location = LocationBuilder(organization).with_long_lat(a_nearby_point[0], a_nearby_point[1]).create()
        set_location_for_service(a_nearby_service.id, location.id)

        a_further_away_service = ServiceBuilder(organization).create()
        location = LocationBuilder(organization).with_long_lat(a_further_away_point[0], a_further_away_point[1]).create()
        set_location_for_service(a_further_away_service.id, location.id)

        a_far_away_service = ServiceBuilder(organization).create()
        location = LocationBuilder(organization).with_long_lat(a_far_away_point[0], a_far_away_point[1]).create()
        set_location_for_service(a_far_away_service.id, location.id)

        topic_id = a_string()
        create_topic(topic_id)
        set_service_similarity_score(topic_id, a_far_away_service.id, 0.9)
        set_service_similarity_score(topic_id, a_nearby_service.id, 0.9)
        set_service_similarity_score(topic_id, a_further_away_service.id, 0.9)

        response = self.make_service_request(topic_id, a_point)

        try:
            parsed_response = json.loads(response)
            self.assertEqual(len(parsed_response['results']), 3)
            self.assertEqual(parsed_response['results'][0]['service']['id'], a_nearby_service.id)
            self.assertEqual(parsed_response['results'][1]['service']['id'], a_far_away_service.id)
            self.assertEqual(parsed_response['results'][2]['service']['id'], a_further_away_service.id)
        except json.decoder.JSONDecodeError:
            print('Error parsing JSON')
            print(response)

    def test_only_return_services_located_within_25_km_of_user_location(self):
        if not os.path.isfile('./run_integration_tests'):
            return

        a_point = (-119.741616, 46.752271)
        a_point_20_km_away = (-119.613355, 46.595071)
        a_point_29_km_away = (-119.559918, 46.523142)

        organization = OrganizationBuilder().create()

        a_service_20_km_away = ServiceBuilder(organization).create()
        location = LocationBuilder(organization).with_long_lat(a_point_20_km_away[0], a_point_20_km_away[1]).create()
        set_location_for_service(a_service_20_km_away.id, location.id)

        a_service_29_km_away = ServiceBuilder(organization).create()
        location = LocationBuilder(organization).with_long_lat(a_point_29_km_away[0], a_point_29_km_away[1]).create()
        set_location_for_service(a_service_29_km_away.id, location.id)

        topic_id = a_string()
        create_topic(topic_id)
        set_service_similarity_score(topic_id, a_service_20_km_away.id, 0.9)
        set_service_similarity_score(topic_id, a_service_29_km_away.id, 0.9)

        response = self.make_service_request(topic_id, a_point)

        try:
            parsed_response = json.loads(response)
            self.assertEqual(len(parsed_response['results']), 1)
            self.assertEqual(parsed_response['results'][0]['service']['id'], a_service_20_km_away.id)
        except json.decoder.JSONDecodeError:
            print('Error parsing JSON')
            print(response)
