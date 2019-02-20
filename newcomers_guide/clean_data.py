import re


def clean_up_newlines(text):
    text = replace_unicode_newlines(text)
    text = remove_carriage_returns(text)
    text = remove_whitespace_between_newlines(text)
    text = remove_duplicate_space_within_lines(text)
    text = protect_newline_after_whitespace(text)
    text = protect_newlines_around_indented_lines(text)
    text = protect_newlines_around_headings(text)
    text = protect_newlines_around_bullet_list_items(text)
    text = protect_newlines_around_numbered_list_items(text)
    text = protect_multiple_newlines(text)
    text = replace_newlines_with_space(text)
    return unprotect_newlines(text)


def replace_unicode_newlines(text):
    unicode_newline = r'\u2028'
    return re.sub(unicode_newline, r'\n', text)


def remove_carriage_returns(text):
    carriage_return = r'\r'
    return re.sub(carriage_return, r'', text)


def remove_whitespace_between_newlines(text):
    whitespace_between_newlines = r'\n[ \t\r]+\n'
    return re.sub(whitespace_between_newlines, r'\n\n', text)


def remove_duplicate_space_within_lines(text):
    duplicate_spaces = r'([^\n ]) {2,}'
    return re.sub(duplicate_spaces, r'\1 ', text)


def protect_multiple_newlines(text):
    two_or_more_newlines = r'(\n){2,}'
    return re.sub(two_or_more_newlines, r'NEWLINE_MARKERNEWLINE_MARKER', text)


def protect_newline_after_whitespace(text):
    space_and_newline = r'([ \t]+)\n'
    return re.sub(space_and_newline, r'\1NEWLINE_MARKER', text)


def protect_newlines_around_indented_lines(text):
    at_text_start = r'^([\t ][^\n]+)\n'
    text = re.sub(at_text_start, r'\1NEWLINE_MARKER', text)

    at_line_start = r'\n([\t ][^\n])'
    text = re.sub(at_line_start, r'NEWLINE_MARKER\1', text)

    at_line_end = r'(NEWLINE_MARKER[\t ][^\n]+)\n'
    return re.sub(at_line_end, r'\1NEWLINE_MARKER', text)


def protect_newlines_around_headings(text):
    at_text_start = r'^(#[^\n]+)\n+'
    text = re.sub(at_text_start, r'\1NEWLINE_MARKER', text)

    at_line_start = r'\n(#[^\n])'
    text = re.sub(at_line_start, r'NEWLINE_MARKER\1', text)

    at_line_end = r'(NEWLINE_MARKER#[^\n]+)\n+'
    return re.sub(at_line_end, r'\1NEWLINE_MARKER', text)


def protect_newlines_around_bullet_list_items(text):
    # This regex matches the last item in a bullet list:
    # a new line, optional white space, a bullet character,
    # one or more non-empty lines, an empty line
    last_list_item = r'(\n[ \t]*[\*\+\-]([^\n]+\n)+)\n'
    text = re.sub(last_list_item, r'\1SECOND_NEWLINE', text)
    text = re.sub(r'\nSECOND_NEWLINE', r'NEWLINE_MARKERNEWLINE_MARKER', text)

    at_line_start = r'\n([\*\+\-][^\n])'
    return re.sub(at_line_start, r'NEWLINE_MARKER\1', text)


def protect_newlines_around_numbered_list_items(text):
    # This regex matches the last item in a numbered list:
    # a new line, optional white space, one or more digits,
    # '.' or ')', one or more non-empty lines, an empty line
    last_list_item = r'(\n[ \t]*\d+[\.\)]([^\n]+\n)+)\n'
    text = re.sub(last_list_item, r'\1SECOND_NEWLINE', text)
    text = re.sub(r'\nSECOND_NEWLINE', r'NEWLINE_MARKERNEWLINE_MARKER', text)

    at_line_start = r'\n(\d+[\.\)][^\n])'
    return re.sub(at_line_start, r'NEWLINE_MARKER\1', text)


def replace_newlines_with_space(text):
    return re.sub(r'\n', r' ', text)


def unprotect_newlines(text):
    return re.sub(r'NEWLINE_MARKER', r'\n', text)


def clean_up_http_links(text):
    return re.sub(r'(https?://[^\s/][^\s]*[a-zA-Z])', r'[link](\1)', text)


def clean_up_email_links(text):
    return re.sub(r'([a-zA-Z]+@[^@\s]+\.[^@\s]+[a-zA-Z])', r'[email](mailto:\1)', text)


def clean_text(text):
    text = clean_up_newlines(text)
    text = clean_up_http_links(text)
    text = clean_up_email_links(text)
    text = add_hashtag_to_headings(text)
    return text

def add_hashtag_to_headings(text):
    heading_at_text_start = r'^([#]+)'
    text = re.sub(heading_at_text_start, r'#\1', text)
    heading_at_line_start = r'(\n[#]+)'
    return re.sub(heading_at_line_start, r'\1#', text)
