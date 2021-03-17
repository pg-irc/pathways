from django.test import TestCase
import re
from newcomers_guide.split_win_file import is_chapter, is_title, is_tag, get_chapter, get_title, get_tags, parse_string


class TestSplitWinFile(TestCase):

    def test_can_identify_chapter_title(self):
        self.assertTrue(is_chapter('8 CHAPTER 8 - Driving'))
        self.assertTrue(is_chapter('1 CHAPTER 1 - Getting Started'))
        self.assertTrue(is_chapter('5 CHAPTER 5 - Health Care'))

    def test_can_get_chapter_title(self):
        self.assertEqual(get_chapter('8 CHAPTER 8 - Driving'), 'CHAPTER 8 - Driving')
        self.assertEqual(get_chapter('5 CHAPTER 5 - Health Care'), 'CHAPTER 5 - Health Care')

    def test_error_on_empty_chapter_title(self):
        with self.assertRaises(RuntimeError):
            get_chapter('8 CHAPTER 8')

    def test_can_identify_topic_title(self):
        self.assertTrue(is_title('2.28 Topic: Places of Worship'))

    def test_topic_title_may_have_no_leading_number(self):
        self.assertTrue(is_title('Topic: Places of Worship'))

    def test_topic_title_can_be_empty(self):
        self.assertTrue(is_title('2.28 Topic: '))

    def test_topic_cannot_have_leading_arbitrary_text(self):
        self.assertFalse(is_title('Bla Topic: '))

    def test_can_get_title_string(self):
        self.assertEqual(get_title('Topic: Places of Worship'), 'Places of Worship')

    def test_error_on_empty_title(self):
        with self.assertRaises(RuntimeError):
            get_title('Topic:')

    def test_can_identify_topic_tags(self):
        self.assertTrue(is_tag('Tags: healthCare:disability'))

    def test_can_get_zero_tags(self):
        self.assertEqual(get_tags('Tags:'), [])

    def test_can_get_one_tag(self):
        self.assertEqual(get_tags('Tags: healthCare:disability'), ['healthCare:disability'])

    def test_can_get_multiple_tags(self):
        self.assertEqual(get_tags('Tags: healthCare:disability housing:wantToBuy'), ['healthCare:disability',
                                                                                     'housing:wantToBuy'])

    def test_can_get_topic_from_line(self):
        data = '2.20 Topic: Places of Worship\nsome more text goes here'
        writer = parse_string(data)
        self.assertEqual(len(writer.topics), 1)
        self.assertEqual(writer.topics[0].topic, 'Places of Worship')

    def test_can_get_tags_from_line(self):
        data = '2.20 Topic: Places of Worship\nTags: first:tag second:tag\nsome more text goes here'
        writer = parse_string(data)
        self.assertEqual(len(writer.topics), 1)
        self.assertEqual(writer.topics[0].tags, ['first:tag', 'second:tag'])

    def test_can_get_text_from_line(self):
        data = '2.20 Topic: Places of Worship\nTags: first:tag second:tag\nsome more text goes here'
        writer = parse_string(data)
        self.assertEqual(len(writer.topics), 1)
        self.assertEqual(writer.topics[0].text, 'some more text goes here\n')

    def test_can_get_multiple_lines_of_text(self):
        data = '2.20 Topic: Places of Worship\nTags: first:tag second:tag\nsome more text goes here\nand here\nand then some more'
        writer = parse_string(data)
        self.assertEqual(len(writer.topics), 1)
        self.assertEqual(writer.topics[0].text, 'some more text goes here\nand here\nand then some more\n')

    def test_can_get_two_topics_from_lines(self):
        data = ('2.10 Topic: Biking\nTags: transport:local\nBiking is fun\n2.11 Topic: Travel by plane\n'
                'Tags: transport:long_distance\nPlanes fly fast\n')
        writer = parse_string(data)
        self.assertEqual(len(writer.topics), 2)
        self.assertEqual(writer.topics[0].topic, 'Biking')
        self.assertEqual(writer.topics[1].topic, 'Travel by plane')

    def test_can_get_chapter_name(self):
        data = '8 CHAPTER 8 - Driving\nTopic: Places of worship'
        writer = parse_string(data)
        self.assertEqual(writer.topics[0].chapter, 'CHAPTER 8 - Driving')

    def test_chapter_name_applies_to_several_topics(self):
        data = ('8 CHAPTER 8 - Driving\n'
                '1.23 Topic: First topic\n'
                'Some text\n'
                '1.24 Topic: Second topic\n'
                'Some more text')
        writer = parse_string(data)
        self.assertEqual(writer.topics[0].chapter, 'CHAPTER 8 - Driving')
        self.assertEqual(writer.topics[1].chapter, 'CHAPTER 8 - Driving')

    def test_compute_file_path(self):
        data = ('8 CHAPTER 8 - Driving\n1.23 Topic: Buying a new or used vehicle (car or truck)\nTags: explore:driving driving:cost\nThis is about driving\n')
        writer = parse_string(data)
        self.assertEqual(writer.topics[0].file_path(), 'mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/')

    def test_compute_file_name(self):
        data = ('8 CHAPTER 8 - Driving\n1.23 Topic: Buying a new or used vehicle (car or truck)\nTags: explore:driving driving:cost\nThis is about driving\n')
        writer = parse_string(data)
        self.assertEqual(writer.topics[0].file_name(), 'mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/en.Buying a new or used vehicle (car or truck).md')

    def test_throw_error_on_empty_chapter(self):
        data = '1.23 Topic: Topic name\nTags: first:tag second:tag\nSome text'
        writer = parse_string(data)
        with self.assertRaises(RuntimeError):
            writer.topics[0].file_name()

    def test_throw_error_on_slash_in_chapter(self):
        data = '8 CHAPTER 8 - The Chapter/name\n1.23 Topic: This That\nSome text'
        writer = parse_string(data)
        with self.assertRaises(RuntimeError):
            writer.topics[0].file_name()

    def test_throw_error_on_slash_in_topic(self):
        data = '8 CHAPTER 8 - The Chapter\n1.23 Topic: This/That\nSome text'
        writer = parse_string(data)
        with self.assertRaises(RuntimeError):
            writer.topics[0].file_name()

    def test_prepend_root_to_path(self):
        data = ('8 CHAPTER 8 - Driving\n1.23 Topic: Buying a new or used vehicle (car or truck)\nTags: explore:driving driving:cost\nThis is about driving\n')
        writer = parse_string(data)
        root = 'theRoot'
        self.assertEqual(writer.topics[0].file_path(root), 'theRoot/mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/')
        self.assertEqual(writer.topics[0].file_name(root), 'theRoot/mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/en.Buying a new or used vehicle (car or truck).md')

    def test_can_pass_locale_for_output_filename(self):
        data = ('8 CHAPTER 8 - Driving\n1.23 Topic: Buying a new or used vehicle (car or truck)\nTags: explore:driving driving:cost\nThis is about driving\n')
        writer = parse_string(data)
        root = 'theRoot'
        self.assertEqual(writer.topics[0].file_name(root, 'xy'), 'theRoot/mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/xy.Buying a new or used vehicle (car or truck).md')

    def test_can_compute_taxonomy_file_name(self):
        data = ('8 CHAPTER 8 - Driving\n1.23 Topic: Buying a new or used vehicle (car or truck)\nTags: explore:driving driving:cost\nThis is about driving\n')
        writer = parse_string(data)
        root = 'theRoot'
        self.assertEqual(writer.topics[0].taxonomy_file_name(root), 'theRoot/mb/CHAPTER 8 - Driving/topics/Buying a new or used vehicle (car or truck)/taxonomy.txt')

    def test_can_get_taxonomy_terms_for_output(self):
        data = '8 CHAPTER 8 - Driving\n1.23 Topic: The topic\nTags: healthCare:disability housing:wantToBuy'
        writer = parse_string(data)
        self.assertEqual(writer.topics[0].tags_for_writing(), 'healthCare:disability, housing:wantToBuy')
