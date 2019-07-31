from bc211 import dtos
from human_services.organizations import models
from common.testhelpers.random_test_values import a_string, a_website_address, an_email_address


class OrganizationBuilder:
    def __init__(self):
        self.organization_id = a_string()
        self.name = a_string()
        self.description = a_string()
        self.website = a_website_address()
        self.email = an_email_address()

    def with_id(self, organization_id):
        self.organization_id = organization_id
        return self

    def with_name(self, name):
        self.name = name
        return self

    def with_description(self, description):
        self.description = description
        return self

    def with_website(self, website):
        self.website = website
        return self

    def with_email(self, email):
        self.email = email
        return self

    def build(self):
        result = models.Organization()
        result.id = self.organization_id
        result.name = self.name
        result.description = self.description
        result.website = self.website
        result.email = self.email
        return result

    def build_dto(self):
        return dtos.Organization(id=self.organization_id,
                                 name=self.name,
                                 description=self.description,
                                 website=self.website,
                                 email=self.email,
                                 locations=[])

    def create(self):
        result = self.build()
        result.save()
        return result
