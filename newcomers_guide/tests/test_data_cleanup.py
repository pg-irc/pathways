from django.test import TestCase
from newcomers_guide.data_cleanup import clean_up_links, clean_up_newlines


class CleanUpNewlinesTest(TestCase):
    def test_replaces_single_newline_with_space(self):
        text = 'abc\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc def')

    def test_replaces_single_newline_in_two_places_with_spaces(self):
        text = 'abc\ndef\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc def ghi')

    def test_replaces_one_newline_surrounded_by_whitspace(self):
        text = 'abc\t \n\r\t def'
        self.assertEqual(clean_up_newlines(text), 'abc def')

    def test_replaces_double_newline_with_newline(self):
        text = 'abc\n\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\ndef')

    def test_replaces_tripple_newline_with_newline(self):
        text = 'abc\n\n\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\ndef')

    def test_replaces_double_newline_carriage_return_with_newline(self):
        text = 'abc\n\r\n\rdef'
        self.assertEqual(clean_up_newlines(text), 'abc\ndef')


class CleanUpLinksTest(TestCase):
    def test_replaces_http_link_with_markdown(self):
        text = 'abc http://example.com def'
        self.assertEqual(clean_up_links(text), 'abc [example.com](http://example.com) def')

    def test_replaces_two_links_with_markdown(self):
        text = 'abc http://example.com def http://example.org ghi'
        expected = 'abc [example.com](http://example.com) def [example.org](http://example.org) ghi'
        self.assertEqual(clean_up_links(text), expected)

    def test_includes_just_host_in_link_name(self):
        text = 'abc http://example.com/foo/bar def'
        self.assertEqual(clean_up_links(text), 'abc [example.com](http://example.com/foo/bar) def')

    def test_replaces_https_link_with_markdown(self):
        text = 'https://example.com'
        self.assertEqual(clean_up_links(text), '[example.com](https://example.com)')
