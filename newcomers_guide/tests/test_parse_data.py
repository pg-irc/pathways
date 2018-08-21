from django.core import exceptions
from django.test import TestCase
from common.testhelpers.random_test_values import a_string
from newcomers_guide.parse_data import (parse_taxonomy_terms, parse_taxonomy_files,
                                        parse_article_files, parse_task_files, parse_file_path,
                                        TaxonomyTermReference)
from newcomers_guide.generate_fixtures import set_taxonomy_term_references_on_content


class FilePathParseTests(TestCase):
    def setUp(self):
        self.path = 'some/path/chapter_6_education/tasks/To_learn_english/fr.Apprendre l\'anglais.md'
        self.parsed_path = parse_file_path(self.path)

    def test_can_extract_chapter(self):
        self.assertEqual(self.parsed_path.chapter, 'chapter_6_education')

    def test_can_extract_content_type(self):
        self.assertEqual(self.parsed_path.type, 'tasks')

    def test_can_extract_content_id(self):
        self.assertEqual(self.parsed_path.id, 'To_learn_english')

    def test_can_extract_language(self):
        self.assertEqual(self.parsed_path.locale, 'fr')

    def test_can_extract_localized_content_title(self):
        self.assertEqual(self.parsed_path.title, 'Apprendre l\'anglais')

    def test_can_handle_titles_with_period(self):
        path = 'some/path/Chapter 5 - Health Care/articles/B.C. health/en.B.C. health.md'
        parsed_path = parse_file_path(path)
        self.assertEqual(parsed_path.title, 'B.C. health')


class ProcessTaskFilesTests(TestCase):
    def setUp(self):
        self.english_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'

        self.content = a_string()
        self.result = parse_task_files([[self.english_path, self.content]])

    def test_include_content_id_from_path(self):
        self.assertEqual(self.result['taskMap']['To_learn_english']['id'], 'To_learn_english')

    def test_include_localzed_title_from_path(self):
        self.assertEqual(self.result['taskMap']['To_learn_english']['title']['en'], 'Learn_english')

    def test_include_complete_flag(self):
        self.assertEqual(self.result['taskMap']['To_learn_english']['completed'], False)

    def test_handles_unicode_in_title(self):
        self.english_path = "some/path/chapter/tasks/the_id/fr.Système_d'éducation.txt"
        self.result = parse_task_files([[self.english_path, a_string()]])
        self.assertEqual(self.result['taskMap']['the_id']['title']['fr'], "Système_d'éducation")

    def test_include_localzed_content(self):
        self.assertEqual(self.result['taskMap']['To_learn_english']['description']['en'], self.content)

    def test_clean_up_content_linebreaks(self):
        result = parse_task_files([[self.english_path, 'abc \n def']])
        description = result['taskMap']['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc def')

    def test_clean_up_content_links(self):
        result = parse_task_files([[self.english_path, 'abc http://example.com def']])
        description = result['taskMap']['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc [example.com](http://example.com) def')

    def test_handle_localized_titles_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/tasks/To_learn_english/fr.Apprendre_l_anglais.txt'
        result = parse_task_files([[self.english_path, a_string()],
                                   [french_path, a_string()]])
        self.assertEqual(result['taskMap']['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['taskMap']['To_learn_english']['title']['fr'], 'Apprendre_l_anglais')

    def test_handle_localized_description_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/tasks/To_learn_english/fr.Apprendre_l_anglais.txt'
        english_description = a_string()
        french_description = a_string()
        result = parse_task_files([[self.english_path, english_description],
                                   [french_path, french_description]])
        self.assertEqual(result['taskMap']['To_learn_english']['description']['en'], english_description)
        self.assertEqual(result['taskMap']['To_learn_english']['description']['fr'], french_description)

    def test_combine_files_for_different_content(self):
        secondary_path = 'some/path/chapter/tasks/Registering_child_in_school/en.Registering_in_public_school.txt'
        result = parse_task_files([[self.english_path, a_string()],
                                   [secondary_path, a_string()]])
        self.assertEqual(result['taskMap']['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['taskMap']['Registering_child_in_school']
                         ['title']['en'], 'Registering_in_public_school')

    def test_parse_task_files_excludes_nontask_content(self):
        task_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'
        article_path = 'some/path/chapter/articles/Human_rights/en.Human_rights.txt'
        result = parse_task_files([[task_path, a_string()], [article_path, a_string()]])
        self.assertIn('To_learn_english', result['taskMap'])
        self.assertNotIn('Human_rights', result['taskMap'])


class ProcessArticleFilesTests(TestCase):

    def setUp(self):
        self.english_path = 'some/path/chapter/articles/To_learn_english/en.Learn_english.txt'

        self.content = a_string()
        self.result = parse_article_files([[self.english_path, self.content]])

    def test_include_content_id_from_path(self):
        self.assertEqual(self.result['To_learn_english']['id'], 'To_learn_english')

    def test_include_localzed_title_from_path(self):
        self.assertEqual(self.result['To_learn_english']['title']['en'], 'Learn_english')

    def test_handles_unicode_in_title(self):
        self.english_path = "some/path/chapter/articles/the_id/fr.Système_d'éducation.txt"
        self.result = parse_article_files([[self.english_path, a_string()]])
        self.assertEqual(self.result['the_id']['title']['fr'], "Système_d'éducation")

    def test_include_localzed_content(self):
        self.assertEqual(self.result['To_learn_english']['description']['en'], self.content)

    def test_clean_up_content_linebreaks(self):
        result = parse_article_files([[self.english_path, 'abc \n def']])
        description = result['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc def')

    def test_clean_up_content_links(self):
        result = parse_article_files([[self.english_path, 'abc http://example.com def']])
        description = result['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc [example.com](http://example.com) def')

    def test_handle_localized_titles_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/articles/To_learn_english/fr.Apprendre_l_anglais.txt'
        result = parse_article_files([[self.english_path, a_string()],
                                      [french_path, a_string()]])
        self.assertEqual(result['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['To_learn_english']['title']['fr'], 'Apprendre_l_anglais')

    def test_handle_localized_description_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/articles/To_learn_english/fr.Apprendre_l_anglais.txt'
        english_description = a_string()
        french_description = a_string()
        result = parse_article_files([[self.english_path, english_description],
                                      [french_path, french_description]])
        self.assertEqual(result['To_learn_english']['description']['en'], english_description)
        self.assertEqual(result['To_learn_english']['description']['fr'], french_description)

    def test_combine_files_for_different_content(self):
        secondary_path = 'some/path/chapter/articles/Registering_child_in_school/en.Registering_in_public_school.txt'
        result = parse_article_files([[self.english_path, a_string()],
                                      [secondary_path, a_string()]])
        self.assertEqual(result['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['Registering_child_in_school']
                         ['title']['en'], 'Registering_in_public_school')

    def test_parse_article_files_excludes_nonarticle_content(self):
        task_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'
        article_path = 'some/path/chapter/articles/Human_rights/en.Human_rights.txt'
        result = parse_article_files([[task_path, a_string()], [article_path, a_string()]])
        self.assertIn('Human_rights', result)
        self.assertNotIn('To_learn_english', result)


class ParseTaxonomyFileTests(TestCase):
    def test_can_parse_taxonomy_id(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar')[0].taxonomy_id, 'foo')

    def test_can_parse_taxonomy_term_id(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar')[0].taxonomy_term_id, 'bar')

    def test_discards_whitespace(self):
        self.assertEqual(parse_taxonomy_terms(' foo:bar ')[0].taxonomy_term_id, 'bar')

    def test_can_parse_multiple_terms(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar, baz:zup')[1].taxonomy_id, 'baz')

    def test_discards_hierachical_term_as_flat_for_now(self):
        result = parse_taxonomy_terms('foo:bar:baz')
        self.assertEqual(result[0].taxonomy_id, 'foo')
        self.assertEqual(result[0].taxonomy_term_id, 'bar')

    def test_throws_on_space_around_colon_character(self):
        error_message = '"foo :bar" : Invalid taxonomy term format'
        with self.assertRaisesMessage(exceptions.ValidationError, error_message):
            parse_taxonomy_terms('foo :bar')

        error_message = '"foo: bar" : Invalid taxonomy term format'
        with self.assertRaisesMessage(exceptions.ValidationError, error_message):
            parse_taxonomy_terms('foo: bar')


class ProcessAllTaxonomyFilesTests(TestCase):
    def setUp(self):
        self.references = parse_taxonomy_files([['some/path/tasks/TaskId/en.name.txt', 'TaxId:TaxTermId']])

    def test_creates_reference_with_taxonomy_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_id, 'TaxId')

    def test_creates_reference_with_taxonomy_term_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_term_id, 'TaxTermId')

    def test_creates_reference_with_content_type_from_path(self):
        self.assertEqual(self.references[0].content_type, 'tasks')

    def test_creates_reference_with_content_id_from_path(self):
        self.assertEqual(self.references[0].content_id, 'TaskId')

    def test_creates_one_reference_for_each_element_in_content(self):
        self.references = parse_taxonomy_files(
            [['some/path/tasks/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].taxonomy_id, 'FooTaxId')
        self.assertEqual(self.references[1].taxonomy_id, 'BarTaxId')

    def test_all_one_reference_tagged_with_content_id(self):
        self.references = parse_taxonomy_files(
            [['some/path/tasks/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].content_id, 'TaskId')
        self.assertEqual(self.references[1].content_id, 'TaskId')


class SetTaxonomiesOnContentTests(TestCase):
    def test_adds_taxonomy_term_reference_collection_on_task(self):
        taxonomy_reference = TaxonomyTermReference('taxId', 'taxTermId', 'contentType', 'contentId')
        content = {'contentId': {'id': 'contentId'}}
        set_taxonomy_term_references_on_content([taxonomy_reference], content)
        self.assertEqual(content['contentId']['taxonomyTerms'], [
            {
                'taxonomyId': 'taxId',
                'taxonomyTermId': 'taxTermId'
            }])

    def test_appends_taxonomy_term_references_to_existing_collection_on_task(self):
        taxonomy_reference = TaxonomyTermReference('taxId', 'taxTermId', 'contentType', 'contentId')
        content = {'contentId': {'id': 'contentId',
                                 'taxonomyTerms': [{
                                     'taxonomyId': 'fooTaxId',
                                     'taxonomyTermId': 'fooTaxTermId'
                                 }]}}
        set_taxonomy_term_references_on_content([taxonomy_reference], content)
        self.assertEqual(content['contentId']['taxonomyTerms'], [
            {
                'taxonomyId': 'fooTaxId',
                'taxonomyTermId': 'fooTaxTermId'
            },
            {
                'taxonomyId': 'taxId',
                'taxonomyTermId': 'taxTermId'
            }])

    def test_appends_multiple_taxonomy_term_references_to_collection_on_task(self):
        first_taxonomy_reference = TaxonomyTermReference('taxId',
                                                         'taxTermId',
                                                         'contentType',
                                                         'contentId')
        second_taxonomy_reference = TaxonomyTermReference('fooTaxId',
                                                          'fooTaxTermId',
                                                          'contentType',
                                                          'contentId')
        content = {'contentId': {'id': 'contentId'}}
        set_taxonomy_term_references_on_content([first_taxonomy_reference, second_taxonomy_reference], content)
        self.assertEqual(content['contentId']['taxonomyTerms'], [
            {
                'taxonomyId': 'taxId',
                'taxonomyTermId': 'taxTermId'
            },
            {
                'taxonomyId': 'fooTaxId',
                'taxonomyTermId': 'fooTaxTermId'
            }
        ])

    def test_does_not_change_task_with_different_id(self):
        taxonomy_reference = TaxonomyTermReference('taxId',
                                                   'taxTermId',
                                                   'contentType',
                                                   'differentContentId')
        content = {'contentId': {'id': 'contentId'}}
        set_taxonomy_term_references_on_content([taxonomy_reference], content)
        self.assertTrue('taxonomyTerms' not in content['contentId'])
