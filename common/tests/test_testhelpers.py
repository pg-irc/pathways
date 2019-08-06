from django.test import TestCase
from common.testhelpers.random_test_values import a_string, a_list_of_strings, a_list_of_integers, a_phone_number


class TestTestHelpers(TestCase):
    def test_a_string_can_produce_valid_country_code(self):
        a_string_country_code = a_string(2, 'CA')
        possible_country_codes = ['CA', 'AC', 'CC', 'AA']
        return self.assertIn(a_string_country_code, possible_country_codes)

    def test_a_string_by_default_is_20_characters_long(self):
        return self.assertEqual(len(a_string()), 20)

    def test_a_string_by_default_is_alpha(self):
        return self.assertTrue(a_string().isalpha())

    def test_a_string_by_default_is_lower(self):
        return self.assertTrue(a_string().islower())

    def test_a_list_of_strings_by_default_has_length_3(self):
        return self.assertEqual(len(a_list_of_strings()), 3)

    def test_a_list_of_ints_by_default_has_length_3(self):
        return self.assertEqual(len(a_list_of_integers()), 3)

    def test_a_phone_number_by_default_has_length_10(self):
        return self.assertEqual(len(a_phone_number()), 12)

    def test_a_phone_number_is_numeric(self):
        return self.assertFalse(a_phone_number().isnumeric())
