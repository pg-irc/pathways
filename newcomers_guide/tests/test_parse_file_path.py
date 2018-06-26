from django.test import TestCase
from newcomers_guide.parse_file_path import parse_file_path


class FilePathParseTests(TestCase):
    def setUp(self):
        self.path = 'some/path/chapter_6_education/tasks/To_learn_english/fr.Apprendre_l_anglais.txt'
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
        self.assertEqual(self.parsed_path.title, 'Apprendre_l_anglais')
