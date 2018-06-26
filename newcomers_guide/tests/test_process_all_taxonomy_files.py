from django.test import TestCase
from django.core import exceptions
from newcomers_guide.process_all_taxonomy_files import parse_taxonomy_file, process_all_taxonomy_files


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


class ProcessAllTaxonomyFilesTests(TestCase):
    def setUp(self):
        self.references = process_all_taxonomy_files([['some/path/tasks/TaskId/en.name.txt', 'TaxId:TaxTermId']])

    def test_creates_reference_with_taxonomy_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_id, 'TaxId')

    def test_creates_reference_with_taxonomy_term_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_term_id, 'TaxTermId')

    def test_creates_reference_with_content_type_from_path(self):
        self.assertEqual(self.references[0].content_type, 'tasks')

    def test_creates_reference_with_content_id_from_path(self):
        self.assertEqual(self.references[0].content_id, 'TaskId')

    def test_creates_one_reference_for_each_element_in_content(self):
        self.references = process_all_taxonomy_files(
            [['some/path/tasks/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].taxonomy_id, 'FooTaxId')
        self.assertEqual(self.references[1].taxonomy_id, 'BarTaxId')

    def test_all_one_reference_tagged_with_content_id(self):
        self.references = process_all_taxonomy_files(
            [['some/path/tasks/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].content_id, 'TaskId')
        self.assertEqual(self.references[1].content_id, 'TaskId')
