from django.test import TestCase
from django.core import exceptions
from newcomers_guide.process_all_taxonomy_files import parse_taxonomy_file


class ParseTaxonomyFileTests(TestCase):
    def test_can_parse_taxonomy_id(self):
        self.assertEqual(parse_taxonomy_file('foo:bar')[0].taxonomy_id, 'foo')

    def test_can_parse_taxonomy_term_id(self):
        self.assertEqual(parse_taxonomy_file('foo:bar')[0].taxonomy_term_id, 'bar')

    def test_discards_whitespace(self):
        self.assertEqual(parse_taxonomy_file(' foo:bar ')[0].taxonomy_term_id, 'bar')

    def test_can_parse_multiple_terms(self):
        self.assertEqual(parse_taxonomy_file('foo:bar, baz:zup')[1].taxonomy_id, 'baz')

    def test_reads_hierachical_term_as_flat_for_now(self):
        result = parse_taxonomy_file('foo:bar:baz')
        self.assertEqual(result[0].taxonomy_id, 'foo')
        self.assertEqual(result[0].taxonomy_term_id, 'bar:baz')

    def test_throws_on_space_around_colon_character(self):
        error_message = '"foo :bar" : Invalid taxonomy term format'
        with self.assertRaisesMessage(exceptions.ValidationError, error_message):
            parse_taxonomy_file('foo :bar')

        error_message = '"foo: bar" : Invalid taxonomy term format'
        with self.assertRaisesMessage(exceptions.ValidationError, error_message):
            parse_taxonomy_file('foo: bar')
