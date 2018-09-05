from django.test import TestCase
from django.core import exceptions
from human_services.organizations.tests.helpers import OrganizationBuilder
from common.testhelpers.database import validate_save_and_reload


# pylint: disable=too-many-public-methods
class TestOrganizationModel(TestCase):
    def test_has_id_field(self):
        organization_id = 'the_id'
        organization = OrganizationBuilder().with_id(organization_id).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.id, organization_id)

    def test_id_cannot_be_none(self):
        organization_id = None
        organization = OrganizationBuilder().with_id(organization_id).build()
        with self.assertRaises(exceptions.ValidationError):
            organization.full_clean()

    def test_id_cannot_be_empty(self):
        organization_id = ''
        organization = OrganizationBuilder().with_id(organization_id).build()
        with self.assertRaises(exceptions.ValidationError):
            organization.full_clean()

    def test_id_cannot_contain_space(self):
        organization_id = 'the id'
        organization = OrganizationBuilder().with_id(organization_id).build()
        with self.assertRaises(exceptions.ValidationError):
            organization.full_clean()

    def test_has_name_field(self):
        name = 'The name'
        organization = OrganizationBuilder().with_name(name).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.name, name)

    def test_name_is_multilingual(self):
        organization = OrganizationBuilder().build()
        set_name_in_language(organization, 'en', 'In English')
        set_name_in_language(organization, 'fr', 'En français')
        organization_from_db = validate_save_and_reload(organization)

        self.assert_name_in_language_equals(organization_from_db, 'en', 'In English')
        self.assert_name_in_language_equals(organization_from_db, 'fr', 'En français')

    def assert_name_in_language_equals(self, organization, language, expected_text):
        organization.set_current_language(language)
        self.assertEqual(organization.name, expected_text)

    def test_has_description_field(self):
        description = 'The description'
        organization = OrganizationBuilder().with_description(description).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.description, description)

    def test_description_can_be_blank(self):
        description = ''
        organization = OrganizationBuilder().with_description(description).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.description, description)

    def test_description_is_multilingual(self):
        organization = OrganizationBuilder().build()
        set_description_in_language(organization, 'en', 'In English')
        set_description_in_language(organization, 'fr', 'En français')
        organization_from_db = validate_save_and_reload(organization)

        self.assert_description_in_language_equals(organization_from_db, 'en', 'In English')
        self.assert_description_in_language_equals(organization_from_db, 'fr', 'En français')

    def assert_description_in_language_equals(self, organization, language, expected_text):
        organization.set_current_language(language)
        self.assertEqual(organization.description, expected_text)

    def test_has_website_field(self):
        website = 'http://www.example.org'
        organization = OrganizationBuilder().with_website(website).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.website, website)

    def test_website_must_be_valid(self):
        invalid_website = 'not a valid website address'
        organization = OrganizationBuilder().with_website(invalid_website).build()
        with self.assertRaises(exceptions.ValidationError):
            organization.full_clean()

    def test_website_can_be_none(self):
        no_website = None
        organization = OrganizationBuilder().with_website(no_website).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.website, no_website)

    def test_empty_website_is_saved_as_none(self):
        empty_website = ''
        no_website = None
        organization = OrganizationBuilder().with_website(empty_website).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.website, no_website)

    def test_has_email_field(self):
        email = 'someone@example.org'
        organization = OrganizationBuilder().with_email(email).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.email, email)

    def test_email_must_be_valid(self):
        email = 'not a valid email address'
        organization = OrganizationBuilder().with_email(email).build()
        with self.assertRaises(exceptions.ValidationError):
            organization.full_clean()

    def test_email_can_be_empty(self):
        no_email = None
        organization = OrganizationBuilder().with_email(no_email).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.email, no_email)

    def test_empty_email_is_saved_as_none(self):
        empty_email = ''
        no_email = None
        organization = OrganizationBuilder().with_email(empty_email).build()
        organization_from_db = validate_save_and_reload(organization)
        self.assertEqual(organization_from_db.email, no_email)


def set_name_in_language(organization, language, text):
    organization.set_current_language(language)
    organization.name = text

def set_description_in_language(organization, language, text):
    organization.set_current_language(language)
    organization.description = text
