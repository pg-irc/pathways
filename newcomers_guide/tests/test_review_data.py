from django.test import TestCase
from utility.review_data import compare_data, partition_files


class PartitionFilesForReview(TestCase):
    def test_includes_file_in_reference_language(self):
        result = partition_files('en', 'fr', {
            'somePath': ['en.content.md', 'fr.content.md'],
        })
        self.assertEqual(result[0].reference_file, 'somePath/en.content.md')

    def test_includes_file_in_target_language(self):
        result = partition_files('en', 'fr', {
            'somePath': ['en.content.md', 'fr.content.md'],
        })
        self.assertEqual(result[0].target_file, 'somePath/fr.content.md')

    def test_ignore_if_only_reference_file_exists(self):
        result = partition_files('en', 'fr', {
            'somePath': ['en.content.md'],
        })
        self.assertEqual(len(result), 0)

    def test_ignore_if_only_target_file_exists(self):
        result = partition_files('en', 'fr', {
            'somePath': ['fr.content.md'],
        })
        self.assertEqual(len(result), 0)


class CompareDataForReviewTests(TestCase):
    def test_detects_heading_missing_at_start_of_file(self):
        target_text = 'Heading'
        reference_text = '# Heading'
        result = compare_data(target_text, reference_text)
        self.assertRegex(result, r'contains 0 headings, reference has 1')

    def test_ignores_matching_heading(self):
        target_text = 'some text.\n#Heading'
        reference_text = 'some text.\n#Heading'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_heading_missing(self):
        target_text = 'some text.\nHeading'
        reference_text = 'some text.\n#Heading'
        result = compare_data(target_text, reference_text)
        self.assertRegex(result, r'contains 0 headings, reference has 1')

    def test_detects_extra_heading(self):
        target_text = 'some text.\n#Heading'
        reference_text = 'some text.\nHeading'
        result = compare_data(target_text, reference_text)
        self.assertRegex(result, r'contains 1 headings, reference has 0')

    def test_ignores_hash_signs_within_lines(self):
        target_text = 'foo bar baz'
        reference_text = 'foo # bar baz'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_bullet_missing_at_start_of_file(self):
        target_text = 'Bullet'
        reference_text = '* Bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 bullets, reference has 1')

    def test_detects_bullet_missing(self):
        target_text = 'some text.Bullet'
        reference_text = 'some text.\n* Bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 bullets, reference has 1')

    def test_detects_minus_bullet_missing(self):
        target_text = 'some text.Bullet'
        reference_text = 'some text.\n- Bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 bullets, reference has 1')

    def test_detects_plus_bullet_missing(self):
        target_text = 'some text.Bullet'
        reference_text = 'some text.\n+ Bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 bullets, reference has 1')

    def test_ignored_difference_between_bullet_types(self):
        target_text = 'some text.\n* Bullet'
        reference_text = 'some text.\n+ Bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_extra_bullet(self):
        target_text = 'some text.\n* Bullet'
        reference_text = 'some text.\nBullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 1 bullets, reference has 0')

    def test_ignores_bullet_within_lines(self):
        target_text = 'some text. Not a bullet'
        reference_text = 'some text. * Not a bullet'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_numbered_list_item_is_missing(self):
        target_text = 'some text.\nList item'
        reference_text = 'some text.\n12. List item'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 numbered list items, reference has 1')

    def test_detects_extra_numbered_list_item(self):
        target_text = 'some text.\n12. List item'
        reference_text = 'some text.\nList item'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 1 numbered list items, reference has 0')

    def test_ignores_numbered_list_item_within_line(self):
        target_text = 'some text. 12. List item'
        reference_text = 'some text. List item'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_missing_paragraph_break(self):
        target_text = 'One paragraph. A second paragraph'
        reference_text = 'One paragraph.\n\nA second paragraph'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 paragraph breaks, reference has 1')

    def test_detects_extra_paragraph_break(self):
        target_text = 'One paragraph.\n\nA second paragraph'
        reference_text = 'One paragraph. nA second paragraph'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 1 paragraph breaks, reference has 0')

    def test_detects_missing_line_break(self):
        target_text = 'One paragraph. A second paragraph'
        reference_text = 'One paragraph.  \nA second paragraph'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'contains 0 line breaks, reference has 1')

    def test_one_trailing_space_is_not_considered_line_break(self):
        target_text = 'One paragraph. A second paragraph'
        reference_text = 'One paragraph. \nA second paragraph'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_two_newlines_is_not_considered_line_break(self):
        target_text = 'One paragraph. A second paragraph'
        reference_text = 'One paragraph.  \n\nA second paragraph'
        result = compare_data(target_text, reference_text)
        self.assertNotRegex(result, r'line breaks')

    def test_ignores_matching_urls(self):
        target_text = 'http://www.foo.com'
        reference_text = 'http://www.foo.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_ignores_stuff_on_the_next_line(self):
        target_text = 'http://www.foo.com\nFoo'
        reference_text = 'http://www.foo.com\nBar'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_different_urls(self):
        target_text = 'http://www.foo.com'
        reference_text = 'http://www.bar.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, ('contains link     http://www.foo.com\n'
                                  'the reference has http://www.bar.com')
        )

    def test_detects_missing_url(self):
        target_text = ''
        reference_text = 'http://www.bar.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'missing link http://www.bar.com, it\'s there in the reference')

    def test_detects_extra_url(self):
        target_text = 'http://www.bar.com'
        reference_text = ''
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'extra link http://www.bar.com is not there in the reference')

    def test_ignores_matching_email_addresses(self):
        target_text = 'user@foo.com'
        reference_text = 'user@foo.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_different_email_addresses(self):
        target_text = 'user@foo.com'
        reference_text = 'user@bar.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, ('contains email address user@foo.com\n'
                                  'the reference has      user@bar.com')
                        )

    def test_detects_missing_email_address(self):
        target_text = ''
        reference_text = 'user@foo.com'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'missing email address user@foo.com, it\'s there in the reference')

    def test_detects_extra_email_address(self):
        target_text = 'user@foo.com'
        reference_text = ''
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'extra email address user@foo.com is not there in the reference')

    def test_ignores_matching_phone_numbers(self):
        target_text = '888-888-8888'
        reference_text = '888-888-8888'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, '')

    def test_detects_different_phone_number(self):
        target_text = '888-888-8888'
        reference_text = '111-888-8888'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, ('contains phone number 888-888-8888\n'
                                  'the reference has     111-888-8888')
                        )

    def test_detects_mising_phone_number(self):
        target_text = ''
        reference_text = '111-888-8888'
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'missing phone number 111-888-8888, it\'s there in the reference')

    def test_detects_extra_phone_number(self):
        target_text = '111-888-8888'
        reference_text = ''
        result = compare_data(target_text, reference_text)
        self.assertEqual(result, 'extra phone number 111-888-8888 is not there in the reference')

    def test_multiple_differences_are_joined_with_newline(self):
        target_text = 'some text http://www.example.com 1-800-345-6789'
        reference_text = 'some different text http://www.example2.com 1-800-987-6543'
        result = compare_data(target_text, reference_text)
        self.assertEqual(
            result,
            ('contains link     http://www.example.com\n'
             'the reference has http://www.example2.com\n\n'
             'contains phone number 1-800-345-6789\n'
             'the reference has     1-800-987-6543')
        )
