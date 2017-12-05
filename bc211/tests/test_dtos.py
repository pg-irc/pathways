import unittest
from bc211 import dtos, exceptions

class TestSpatialLocation(unittest.TestCase):
    def test_can_create(self):
        location = dtos.SpatialLocation('123.456', '-23.456')
        self.assertAlmostEqual(location.latitude, 123.456)
        self.assertAlmostEqual(location.longitude, -23.456)

    def test_throws_on_latitude_not_a_number(self):
        with self.assertRaises(exceptions.InvalidFloatXmlParseException):
            dtos.SpatialLocation('foo', '-23.456')

    def test_throws_on_longitude_not_a_number(self):
        with self.assertRaises(exceptions.InvalidFloatXmlParseException):
            dtos.SpatialLocation('123.456', 'foo')
