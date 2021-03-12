from django.core import exceptions
from django.test import TestCase
from common.testhelpers.random_test_values import a_string, a_float
from newcomers_guide.parse_data import (parse_taxonomy_terms, parse_taxonomy_files,
                                        parse_topic_files, parse_file_path, TaxonomyTermReference)
from newcomers_guide.generate_fixtures import set_taxonomy_term_references_on_content
from search.models import TaskSimilarityScore
from newcomers_guide.tests.helpers import create_topic


class FilePathParseTests(TestCase):
    def setUp(self):
        self.path = 'some/path/chapter_6_education/topics/To_learn_english/fr.Apprendre l\'anglais.md'
        self.parsed_path = parse_file_path(self.path)

    def test_can_extract_chapter(self):
        self.assertEqual(self.parsed_path.chapter, 'chapter_6_education')

    def test_can_extract_content_type(self):
        self.assertEqual(self.parsed_path.type, 'topics')

    def test_can_extract_content_id(self):
        self.assertEqual(self.parsed_path.id, 'to_learn_english')

    def test_can_extract_language(self):
        self.assertEqual(self.parsed_path.locale, 'fr')

    def test_can_extract_localized_content_title(self):
        self.assertEqual(self.parsed_path.title, 'Apprendre l\'anglais')

    def test_can_handle_titles_with_period(self):
        path = 'some/path/chapter/topics/articleId/en.article.name.with.periods.md'
        parsed_path = parse_file_path(path)
        self.assertEqual(parsed_path.title, 'article.name.with.periods')

    def test_throw_if_filename_contains_one_period(self):
        path = 'some/path/chapter/topics/articleId/name.md'
        with self.assertRaisesMessage(exceptions.ValidationError, 'name.md: Invalid file name'):
            parse_file_path(path)

    def test_throw_if_filename_contains_empty_language_code(self):
        path = 'some/path/chapter/topics/articleId/.name.md'
        with self.assertRaisesMessage(exceptions.ValidationError, '.name.md: Invalid file name'):
            parse_file_path(path)

    def test_throw_if_filename_contains_empty_article_name(self):
        path = 'some/path/chapter/topics/articleId/en..md'
        with self.assertRaisesMessage(exceptions.ValidationError, 'en..md: Invalid file name'):
            parse_file_path(path)

    def test_dont_throw_on_non_content_file(self):
        path = 'some/path/chapter/topics/articleId/en.txt'
        parse_file_path(path)


class ProcessTaskFilesTests(TestCase):
    def setUp(self):
        self.english_path = 'some/path/bc/chapter 5 - driving/topics/To_learn_english/en.Learn_english.txt'

        self.content = a_string()
        self.result = parse_topic_files([[self.english_path, self.content]])

    def test_include_content_id_from_path(self):
        self.assertEqual(self.result['taskMap']['to_learn_english']['id'], 'to_learn_english')

    def test_include_localzed_title_from_path(self):
        self.assertEqual(self.result['taskMap']['to_learn_english']['title']['en'], 'Learn_english')

    def test_include_region_from_path(self):
        self.assertEqual(self.result['taskMap']['to_learn_english']['region'], 'bc')

    def test_include_isNewlyRecommended_flag(self):
        self.assertEqual(self.result['taskMap']['to_learn_english']['isNewlyRecommended'], False)

    def test_handles_unicode_in_title(self):
        self.english_path = "some/path/chapter/topics/the_id/fr.Système_d'éducation.txt"
        self.result = parse_topic_files([[self.english_path, a_string()]])
        self.assertEqual(self.result['taskMap']['the_id']['title']['fr'], "Système_d'éducation")

    def test_include_localzed_content(self):
        self.assertEqual(self.result['taskMap']['to_learn_english']['description']['en'], self.content)

    def test_clean_up_content_linebreaks(self):
        result = parse_topic_files([[self.english_path, 'abc\ndef']])
        description = result['taskMap']['to_learn_english']['description']['en']
        self.assertEqual(description, 'abc def')

    def test_clean_up_content_links(self):
        result = parse_topic_files([[self.english_path, 'abc http://example.com def']])
        description = result['taskMap']['to_learn_english']['description']['en']
        self.assertEqual(description, 'abc [http://example.com](http://example.com) def')

    def test_handle_localized_titles_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter 5 - driving/topics/To_learn_english/fr.Apprendre_l_anglais.txt'
        result = parse_topic_files([[self.english_path, a_string()],
                                    [french_path, a_string()]])
        self.assertEqual(result['taskMap']['to_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['taskMap']['to_learn_english']['title']['fr'], 'Apprendre_l_anglais')

    def test_handle_localized_description_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter 5 - driving/topics/To_learn_english/fr.Apprendre_l_anglais.txt'
        english_description = a_string()
        french_description = a_string()
        result = parse_topic_files([[self.english_path, english_description],
                                    [french_path, french_description]])
        self.assertEqual(result['taskMap']['to_learn_english']['description']['en'], english_description)
        self.assertEqual(result['taskMap']['to_learn_english']['description']['fr'], french_description)

    def test_includes_related_topics_from_database_in_order_of_declining_similarity_score(self):
        topic_id = a_string()
        similar_topic_id = a_string()
        create_topic(topic_id)
        create_topic(similar_topic_id)

        a_high_score = 0.9
        TaskSimilarityScore(first_task_id=topic_id,
                            second_task_id=similar_topic_id,
                            similarity_score=a_high_score).save()

        dissimilar_topic_id = a_string()
        create_topic(dissimilar_topic_id)
        a_low_score = 0.1
        TaskSimilarityScore(first_task_id=topic_id,
                            second_task_id=dissimilar_topic_id,
                            similarity_score=a_low_score).save()

        path = 'some/path/chapter/topics/{0}/en.Learn_english.txt'.format(topic_id)
        result = parse_topic_files([[path, a_string()]])
        self.assertEqual(result['taskMap'][topic_id]['relatedTopics'], [similar_topic_id, dissimilar_topic_id])

    def test_combine_files_for_different_content(self):
        secondary_path = 'some/path/chapter/topics/Registering_child_in_school/en.Registering_in_public_school.txt'
        result = parse_topic_files([[self.english_path, a_string()],
                                    [secondary_path, a_string()]])
        self.assertEqual(result['taskMap']['to_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['taskMap']['registering_child_in_school']
                         ['title']['en'], 'Registering_in_public_school')

    def test_throw_on_same_topic_id_in_different_chapters(self):
        first_path = 'some/path/chapter1/topics/Registering_child_in_school/en.InEnglish.md'
        second_path = 'some/path/chapter2/topics/Registering_child_in_school/fr.InFrench.md'
        error_message = 'registering_child_in_school: don\'t use the same topic id in different chapters'
        with self.assertRaisesMessage(exceptions.ValidationError, error_message):
            parse_topic_files([[first_path, a_string()], [second_path, a_string()]])

    def test_parse_topic_files_includes_article_content(self):
        topic_path = 'some/path/chapter/topics/To_learn_english/en.Learn_english.txt'
        article_path = 'some/path/chapter/topics/Human_rights/en.Human_rights.txt'
        result = parse_topic_files([[topic_path, a_string()], [article_path, a_string()]])
        self.assertIn('to_learn_english', result['taskMap'])
        self.assertIn('human_rights', result['taskMap'])


class ParseTaxonomyFileTests(TestCase):
    def test_can_parse_taxonomy_id(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar')[0].taxonomy_id, 'foo')

    def test_can_parse_taxonomy_term_id(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar')[0].taxonomy_term_id, 'bar')

    def test_discards_whitespace(self):
        self.assertEqual(parse_taxonomy_terms(' foo:bar ')[0].taxonomy_term_id, 'bar')

    def test_discards_newlines(self):
        self.assertEqual(parse_taxonomy_terms('foo:bar\n')[0].taxonomy_term_id, 'bar')

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
        self.references = parse_taxonomy_files([['some/path/topics/TaskId/en.name.txt', 'TaxId:TaxTermId']])

    def test_creates_reference_with_taxonomy_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_id, 'TaxId')

    def test_creates_reference_with_taxonomy_term_id_from_file_content(self):
        self.assertEqual(self.references[0].taxonomy_term_id, 'TaxTermId')

    def test_creates_reference_with_content_type_from_path(self):
        self.assertEqual(self.references[0].content_type, 'topics')

    def test_creates_reference_with_content_id_from_path(self):
        self.assertEqual(self.references[0].content_id, 'taskid')

    def test_creates_one_reference_for_each_element_in_content(self):
        self.references = parse_taxonomy_files(
            [['some/path/topics/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].taxonomy_id, 'FooTaxId')
        self.assertEqual(self.references[1].taxonomy_id, 'BarTaxId')

    def test_all_one_reference_tagged_with_content_id(self):
        self.references = parse_taxonomy_files(
            [['some/path/topics/TaskId/en.name.txt', 'FooTaxId:FooTaxTermId, BarTaxId:BarTaxTermId']])
        self.assertEqual(self.references[0].content_id, 'taskid')
        self.assertEqual(self.references[1].content_id, 'taskid')


class SetTaxonomiesOnContentTests(TestCase):
    def test_adds_taxonomy_term_reference_collection_on_topic(self):
        taxonomy_reference = TaxonomyTermReference('taxId', 'taxTermId', 'contentType', 'contentId')
        content = {'contentId': {'id': 'contentId'}}
        set_taxonomy_term_references_on_content([taxonomy_reference], content)
        self.assertEqual(content['contentId']['taxonomyTerms'], [
            {
                'taxonomyId': 'taxId',
                'taxonomyTermId': 'taxTermId'
            }])

    def test_appends_taxonomy_term_references_to_existing_collection_on_topic(self):
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

    def test_appends_multiple_taxonomy_term_references_to_collection_on_topic(self):
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

    def test_does_not_change_topic_with_different_id(self):
        taxonomy_reference = TaxonomyTermReference('taxId',
                                                   'taxTermId',
                                                   'contentType',
                                                   'differentContentId')
        content = {'contentId': {'id': 'contentId'}}
        set_taxonomy_term_references_on_content([taxonomy_reference], content)
        self.assertTrue('taxonomyTerms' not in content['contentId'])
