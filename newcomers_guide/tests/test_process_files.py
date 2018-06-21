from django.test import TestCase
from newcomers_guide.process_files import process_all_task_files
from common.testhelpers.random_test_values import a_string


class ProcessMultipleFileTest(TestCase):
    def setUp(self):
        self.english_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'

        self.content = a_string()
        self.result = process_all_task_files([[self.english_path, self.content]])

    def test_include_content_id_from_path(self):
        self.assertEqual(self.result['To_learn_english']['id'], 'To_learn_english')

    def test_include_localzed_title_from_path(self):
        self.assertEqual(self.result['To_learn_english']['title']['en'], 'Learn_english')

    def test_handles_unicode_in_title(self):
        self.english_path = "some/path/chapter/tasks/the_id/fr.Système_d'éducation.txt"
        self.result = process_all_task_files([[self.english_path, a_string()]])
        self.assertEqual(self.result['the_id']['title']['fr'], "Système_d'éducation")

    def test_include_localzed_content(self):
        self.assertEqual(self.result['To_learn_english']['description']['en'], self.content)

    def test_clean_up_content_linebreaks(self):
        result = process_all_task_files([[self.english_path, 'abc \n def']])
        description = result['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc def')

    def test_clean_up_content_links(self):
        result = process_all_task_files([[self.english_path, 'abc http://example.com def']])
        description = result['To_learn_english']['description']['en']
        self.assertEqual(description, 'abc [example.com](http://example.com) def')

    def test_handle_localized_titles_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/tasks/To_learn_english/fr.Apprendre_l_anglais.txt'
        result = process_all_task_files([[self.english_path, a_string()],
                                         [french_path, a_string()]])
        self.assertEqual(result['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['To_learn_english']['title']['fr'], 'Apprendre_l_anglais')

    def test_handle_localized_description_when_processing_the_same_content_in_different_locales(self):
        french_path = 'some/path/chapter/tasks/To_learn_english/fr.Apprendre_l_anglais.txt'
        english_description = a_string()
        french_description = a_string()
        result = process_all_task_files([[self.english_path, english_description],
                                         [french_path, french_description]])
        self.assertEqual(result['To_learn_english']['description']['en'], english_description)
        self.assertEqual(result['To_learn_english']['description']['fr'], french_description)

    def test_combine_files_for_different_content(self):
        secondary_path = 'some/path/chapter/tasks/Registering_your_child_in_a_public_school/en.Registering_your_child_in_a_public_school.txt'
        result = process_all_task_files([[self.english_path, a_string()],
                                         [secondary_path, a_string()]])
        self.assertEqual(result['To_learn_english']['title']['en'], 'Learn_english')
        self.assertEqual(result['Registering_your_child_in_a_public_school']['title']
                         ['en'], 'Registering_your_child_in_a_public_school')

    def test_exclude_nontask_content(self):
        task_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'
        article_path = 'some/path/chapter/articles/Human_rights/en.Human_rights.txt'
        result = process_all_task_files([[task_path, a_string()], [article_path, a_string()]])
        self.assertIn('To_learn_english', result)
        self.assertNotIn('Human_rights', result)
