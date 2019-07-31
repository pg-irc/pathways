from bc211 import dtos
from common.testhelpers.random_test_values import a_string, a_point
from django.contrib.gis.geos import Point
from human_services.locations.models import Location


class LocationBuilder:
    def __init__(self, organization):
        self.location_id = a_string()
        self.organization = organization
        self.name = a_string()
        self.point = a_point()
        self.description = a_string()

    def with_id(self, location_id):
        self.location_id = location_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_long_lat(self, longitude, latitude):
        self.point = Point(longitude, latitude)
        return self

    def with_point(self, point):
        self.point = point
        return self

    def with_description(self, description):
        self.description = description
        return self

    def build(self):
        result = Location()
        result.id = self.location_id
        result.name = self.name
        result.organization = self.organization
        result.point = self.point
        result.description = self.description
        return result

    def build_dto(self):
        return dtos.Location(id=self.location_id,
                             name=self.name,
                             organization_id=self.organization.id,
                             description=self.description,
                             spatial_location=None,
                             services=[],
                             physical_address=None,
                             postal_address=None,
                             phone_numbers=[])

    def create(self):
        result = self.build()
        result.save()
        return result
