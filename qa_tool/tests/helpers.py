from qa_tool import models
from common.testhelpers.random_test_values import a_string, a_point, a_website_address, an_integer
from django.contrib.gis.geos import Point


class AlgorithmBuilder:
    def __init__(self):
        self.id = an_integer()
        self.name = a_string()
        self.url = a_website_address()
        self.notes = a_string()

    def build(self):
        result = models.Algorithm()
        result.id = self.id
        result.name = self.name
        result.url = self.url
        result.notes = self.notes
        return result

    def with_name(self, name):
        self.name = name
        return self

    def with_url(self, url):
        self.url = url
        return self

    def with_notes(self, notes):
        self.notes = notes
        return self

    def create(self):
        result = self.build()
        result.save()
        return result


class SearchLocationBuilder:
    def __init__(self):
        self.name = a_string()
        self.point = a_point()

    def build(self):
        result = models.SearchLocation()
        result.name = self.name
        result.point = self.point
        return result

    def with_name(self, name):
        self.name = name
        return self

    def with_long_lat(self, longitude, latitude):
        self.point = Point(longitude, latitude)
        return self

    def create(self):
        result = self.build()
        result.save()
        return result
