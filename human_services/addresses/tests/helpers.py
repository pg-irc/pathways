import string
from bc211 import dtos
from human_services.addresses import models
from common.testhelpers.random_test_values import a_string


class AddressBuilder:
    def __init__(self):
        self.address = a_string()
        self.city = a_string()
        self.country = a_string(2, string.ascii_uppercase)
        self.attention = a_string()
        self.state_province = a_string()
        self.postal_code = a_string()

    def build(self):
        result = models.Address()
        result.address = self.address
        result.city = self.city
        result.country = self.country
        result.attention = self.attention
        result.state_province = self.state_province
        result.postal_code = self.postal_code
        return result

    def build_dto(self, address_type, location_id):
        return dtos.Address(location_id=location_id,
                            address_type_id=address_type,
                            city=self.city,
                            country=self.country,
                            address_lines=self.address,
                            state_province=self.state_province,
                            postal_code=self.postal_code)

    def with_address(self, address):
        self.address = address
        return self

    def with_city(self, city):
        self.city = city
        return self

    def with_country(self, country):
        self.country = country
        return self

    def with_attention(self, attention):
        self.attention = attention
        return self

    def with_state_province(self, state_province):
        self.state_province = state_province
        return self

    def with_postal_code(self, postal_code):
        self.postal_code = postal_code
        return self

    def create(self):
        self.build().save()
