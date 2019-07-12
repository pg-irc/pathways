from django.test import TestCase
from newcomers_guide.clean_data import (clean_up_http_links, clean_up_email_links,
                                        clean_up_newlines, replace_unicode_newlines,
                                        add_https_to_somelinks)

# Need to replace single newlines with space, except when the line before
# and/or after is a list item or heading. This is because the markdown
# component renders newlines as line breaks, see
# https://github.com/mientjan/react-native-markdown-renderer/issues/74

# To minimize needed content editing, newlines are converted into spaces.
# This script needs to do that, since the markdown component renders
# single newlines as line breaks. By the common mark standard, newlines
# preceeded by at least two spaces are rendered as a line break, so we
# need to keep white-space+newline sequences unchanged. A double newline
# are kept unchanged and they are rendered as a paragraph break. More than
# two newlines in a row are converted to just two newlines.

# So for editors: A newline will be rendered as a spaces. A newline
# preceeded by at least two spaces will be rendered as a line break.
# Double newlines (i.e. an empty line) will be rendered as a paragraph break.

# Need to replace multiple spaces with a single space, because the markdown
# component renders larger horizontal spaces for multiple space characters.
# However, multiple spaces at the start of a line are not changed

# Need to leave all whitespace following one or more newlines unchanged,
# because this whitespace can be meaningful when formatting nested lists.

# One newline is enough before and after headings. Three or more newlines
# in a row is OK, even when they're interspersed with other whitespace


class CleanUpNewlinesTest(TestCase):
    def test_replaces_unicode_newlines(self):
        text = 'abc\u2028def'
        self.assertEqual(replace_unicode_newlines(text), 'abc\ndef')

    def test_removes_carriage_returns(self):
        text = 'abc\rdef'
        self.assertEqual(clean_up_newlines(text), 'abcdef')

    def test_removes_duplicate_spaces(self):
        text = 'abc  def'
        self.assertEqual(clean_up_newlines(text), 'abc def')

    def test_leaves_duplicate_spaces_at_line_start_unchanged(self):
        text = '  abc'
        self.assertEqual(clean_up_newlines(text), '  abc')

    def test_removes_whitespace_between_newlines(self):
        text = 'abc\n\t\r \ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\n\ndef')

    def test_leaves_whitespace_before_newline_unchanged(self):
        text = 'abc\t \ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\t \ndef')

    def test_replaces_single_newline_with_space(self):
        text = 'abc\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc def')

    def test_replaces_single_newline_in_two_places_with_spaces(self):
        text = 'abc\ndef\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc def ghi')

    def test_leaves_double_newline_unchanged(self):
        text = 'abc\n\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\n\ndef')

    def test_leaves_double_newline_unchanged_after_inline_bullet_character(self):
        text = ('a*bc\n\ndef')
        self.assertEqual(clean_up_newlines(text), 'a*bc\n\ndef')

    def test_leaves_double_newline_unchanged_after_inline_number(self):
        text = ('a1.bc\n\ndef')
        self.assertEqual(clean_up_newlines(text), 'a1.bc\n\ndef')

    def test_replaces_tripple_newline_with_double_newline(self):
        text = 'abc\n\n\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\n\ndef')

    def test_replaces_four_newlines_with_double_newline(self):
        text = 'abc\n\n\n\ndef'
        self.assertEqual(clean_up_newlines(text), 'abc\n\ndef')

    def test_leaves_newline_unchanged_before_heading(self):
        text = 'abc\n# def'
        self.assertEqual(clean_up_newlines(text), 'abc\n# def')

    def test_leaves_newline_unchanged_after_heading(self):
        text = 'abc\n# def\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n# def\nghi')
        text = '# def\nghi'
        self.assertEqual(clean_up_newlines(text), '# def\nghi')

    def test_leaves_newline_unchanged_before_star_bullet(self):
        text = 'abc\n* def'
        self.assertEqual(clean_up_newlines(text), 'abc\n* def')

    def test_replaces_newline_with_space_after_star_bullet(self):
        text = 'abc\n* def\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n* def ghi')
        text = '* def\nghi'
        self.assertEqual(clean_up_newlines(text), '* def ghi')

    def test_leaves_newline_unchanged_before_plus_bullet(self):
        text = 'abc\n+ def'
        self.assertEqual(clean_up_newlines(text), 'abc\n+ def')

    def test_replaces_newline_with_space_after_plus_bullet(self):
        text = 'abc\n+ def\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n+ def ghi')
        text = '+ def\nghi'
        self.assertEqual(clean_up_newlines(text), '+ def ghi')

    def test_leaves_newline_unchanged_before_dash_bullet(self):
        text = 'abc\n- def'
        self.assertEqual(clean_up_newlines(text), 'abc\n- def')

    def test_replaces_newline_with_space_after_dash_bullet(self):
        text = 'abc\n- def\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n- def ghi')
        text = '- def\nghi'
        self.assertEqual(clean_up_newlines(text), '- def ghi')

    def test_leaves_double_newline_after_bullet_list_unchanged(self):
        self.maxDiff = None
        text = ('Before list.\n'
                '* First item\n'
                'continues here.\n'
                '* Second item\n'
                'continues here.\n'
                '\n'
                'After list.')
        expected = ('Before list.\n'
                    '* First item continues here.\n'
                    '* Second item continues here.\n'
                    '\n'
                    'After list.')
        self.assertEqual(clean_up_newlines(text), expected)

    def test_leaves_double_newline_after_numbered_list_unchanged(self):
        self.maxDiff = None
        text = ('Before list.\n'
                '1. First item\n'
                'continues here.\n'
                '1. Second item\n'
                'continues here.\n'
                '\n'
                'After list.')
        expected = ('Before list.\n'
                    '1. First item continues here.\n'
                    '1. Second item continues here.\n'
                    '\n'
                    'After list.')
        self.assertEqual(clean_up_newlines(text), expected)

    def test_leaves_newline_unchanged_before_line_starting_with_space(self):
        text = 'abc\n def'
        self.assertEqual(clean_up_newlines(text), 'abc\n def')

    def test_leaves_newline_unchanged_after_line_starting_with_space(self):
        text = 'abc\n def\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n def\nghi')
        text = ' def\nghi'
        self.assertEqual(clean_up_newlines(text), ' def\nghi')

    def test_leaves_newline_unchanged_before_line_starting_with_tab(self):
        text = 'abc\n\tdef'
        self.assertEqual(clean_up_newlines(text), 'abc\n\tdef')

    def test_leaves_newline_unchanged_after_line_starting_with_tab(self):
        text = 'abc\n\tdef\nghi'
        self.assertEqual(clean_up_newlines(text), 'abc\n\tdef\nghi')
        text = '\tdef\nghi'
        self.assertEqual(clean_up_newlines(text), '\tdef\nghi')

    def test_leaves_newline_unchanged_before_numbered_list_item_with_period(self):
        text = 'abc\n123. def'
        self.assertEqual(clean_up_newlines(text), 'abc\n123. def')

    def test_replaces_newline_with_space_after_numbered_list_item_with_period(self):
        text = 'abc\n123. def\nefg'
        self.assertEqual(clean_up_newlines(text), 'abc\n123. def efg')
        text = '123. def\nefg'
        self.assertEqual(clean_up_newlines(text), '123. def efg')

    def test_leaves_newline_unchanged_before_numbered_list_item_with_bracket(self):
        text = 'abc\n123) def'
        self.assertEqual(clean_up_newlines(text), 'abc\n123) def')

    def test_replaces_newline_with_space_after_numbered_list_item_with_bracket(self):
        text = 'abc\n123) def\nefg'
        self.assertEqual(clean_up_newlines(text), 'abc\n123) def efg')
        text = '123) def\nefg'
        self.assertEqual(clean_up_newlines(text), '123) def efg')

    def test_replaces_single_newlines_with_space_also_after_punctuation(self):
        text = 'abc,\r\ndef.\r\nghi)\r\njkl'
        self.assertEqual(clean_up_newlines(text), 'abc, def. ghi) jkl')

    def test_handles_newlines_after_punctuation(self):
        text = 'abc,\r\n\r\ndef.\r\n\r\nghi)\r\n\r\njkl'
        self.assertEqual(clean_up_newlines(text), 'abc,\n\ndef.\n\nghi)\n\njkl')

    # What to do with bullets, throw an error?
    def ignore_test_replaces_bullet_character_with_star(self):
        text = '• This is a bullet'
        self.assertEqual(clean_up_newlines(text), '* This is a bullet')

    def test_leaves_newline_after_heading_unchanged(self):
        text = 'previous paragraph.\n\n# Heading\nBody text.'
        self.assertEqual(clean_up_newlines(text), 'previous paragraph. \n# Heading\nBody text.')

    def test_leaves_newline_after_heading_at_the_start_of_string_unchanged(self):
        text = '# Heading\nBody text.'
        self.assertEqual(clean_up_newlines(text), '# Heading\nBody text.')

    def test_realistic_example(self):
        self.maxDiff = None
        text = ('## Try CommonMark\n\n'
                'You can try CommonMark here.\n'
                'This dingus is powered by\n'
                '[commonmark.js](https://github.com/jgm/commonmark.js), the\n'
                'JavaScript reference implementation.\n'
                '1. item one\n'
                '2. item two\n'
                '   - sublist\n'
                '   - sublist\n')
        expected = ('## Try CommonMark\n'
                    'You can try CommonMark here. This dingus is powered by '
                    '[commonmark.js](https://github.com/jgm/commonmark.js), the '
                    'JavaScript reference implementation.\n'
                    '1. item one\n'
                    '2. item two\n'
                    '   - sublist\n'
                    '   - sublist\n')
        self.assertEqual(clean_up_newlines(text), expected)


class CleanUpUrlLinksTest(TestCase):
    def test_replaces_http_link_with_markdown(self):
        text = 'abc http://example.com def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com](http://example.com) def')

    def test_replaces_two_links_with_markdown(self):
        text = 'abc http://example.com def http://example.org ghi'
        expected = 'abc Web: [http://example.com](http://example.com) def Web: [http://example.org](http://example.org) ghi'
        self.assertEqual(clean_up_http_links(text), expected)

    def test_replaces_https_link_with_markdown(self):
        text = 'https://example.com'
        self.assertEqual(clean_up_http_links(text), 'Web: [https://example.com](https://example.com)')

    def test_handles_urls_with_dash_in_the_host_name(self):
        text = 'http://www.cra-arc.gc.ca/'
        expected = 'Web: [http://www.cra-arc.gc.ca/](http://www.cra-arc.gc.ca/)'
        self.assertEqual(clean_up_http_links(text), expected)

    def test_excludes_trailing_dot_from_link(self):
        text = 'abc http://example.com. Def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com](http://example.com). Def')

    def test_excludes_trailing_comma_from_link(self):
        text = 'abc http://example.com, def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com](http://example.com), def')

    def test_excludes_trailing_closing_parenthesis(self):
        text = 'abc http://example.com) def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com](http://example.com)) def')

    def test_http_link_does_not_truncate_equals_sign(self):
        text = 'abc http://example.com=434 def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com=434](http://example.com=434) def')

    def test_http_link_does_not_truncate_forward_slash(self):
        text = 'abc http://example.com/ def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com/](http://example.com/) def')

    def test_http_link_does_not_truncate_query(self):
        text = 'abc http://foo.com/find?a=a def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://foo.com/find?a=a](http://foo.com/find?a=a) def')

    def test_http_link_does_not_truncate_query_with_ampersand(self):
        text = 'abc http://foo.com/find?a=a&b=b def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://foo.com/find?a=a&b=b](http://foo.com/find?a=a&b=b) def')

    def test_http_link_does_not_truncate_path_ending_with_word_character(self):
        text = 'abc http://example.com/search def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://example.com/search](http://example.com/search) def')

    def test_excludes_trailing_dot_at_end_of_query(self):
        text = 'abc http://foo.com/find?a=a. def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://foo.com/find?a=a](http://foo.com/find?a=a). def')

    def test_excludes_trailing_comma_at_end_of_query(self):
        text = 'abc http://foo.com/find?a=a, def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://foo.com/find?a=a](http://foo.com/find?a=a), def')

    def test_link_at_the_start_of_a_file(self):
        text = 'http://foo.com/find?a=a&b=b def'
        self.assertEqual(clean_up_http_links(text), 'Web: [http://foo.com/find?a=a&b=b](http://foo.com/find?a=a&b=b) def')

    def test_link_at_the_end_of_a_file(self):
        text = 'abc http://foo.com/find?a=a&b=b'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://foo.com/find?a=a&b=b](http://foo.com/find?a=a&b=b)')
    
    def test_http_link_over_28_characters_are_truncated(self):
        text = 'abc http://google.com/search?source=a&page=b def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://google.com/search?sou...](http://google.com/search?source=a&page=b) def')

    def test_http_link_does_not_truncate_long_host_name(self):
        text = 'abc http://excessivelylonghostname.com/search def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [http://excessivelylonghostname.com...](http://excessivelylonghostname.com/search) def')
    
    def test_valid_link_without_http(self):
        text = 'abc www.example.com def'
        self.assertEqual(clean_up_http_links(text), 'abc Web: [https://www.example.com](https://www.example.com) def')

    def test_valid_link_without_http_new_line(self):
        text = 'abc\nwww.example.com def'
        self.assertEqual(clean_up_http_links(text), 'abc\nWeb: [https://www.example.com](https://www.example.com) def')

    def test_invalid_link_without_http(self):
        text = 'abc example.com def'
        self.assertEqual(clean_up_http_links(text), 'abc example.com def')

class CleanUpMailtoLinksTest(TestCase):
    def test_replaces_email_link_with_markdown(self):
        text = 'abc foo@bar.com def'
        self.assertEqual(clean_up_email_links(text), 'abc Email: [foo@bar.com](mailto:foo@bar.com) def')

    def test_excludes_leading_opening_parenthesis(self):
        text = 'abc (foo@bar.com def'
        self.assertEqual(clean_up_email_links(text), 'abc (Email: [foo@bar.com](mailto:foo@bar.com) def')

    def test_excludes_trailing_dot_from_link(self):
        text = 'abc foo@bar.com. Def'
        self.assertEqual(clean_up_email_links(text), 'abc Email: [foo@bar.com](mailto:foo@bar.com). Def')

    def test_excludes_trailing_comma_from_link(self):
        text = 'abc foo@bar.com, def'
        self.assertEqual(clean_up_email_links(text), 'abc Email: [foo@bar.com](mailto:foo@bar.com), def')

    def test_excludes_trailing_closing_parenthesis(self):
        text = 'abc foo@bar.com) def'
        self.assertEqual(clean_up_email_links(text), 'abc Email: [foo@bar.com](mailto:foo@bar.com)) def')
