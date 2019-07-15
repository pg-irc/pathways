import re
from urllib.parse import urlparse

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
    text = add_https_to_somelinks(text)
    return re.sub(r'(https?://[^\s/][^\s]*[a-zA-Z0-9/])', check_length_of_http_links, text)


def clean_up_email_links(text):
    return re.sub(r'([a-zA-Z]+@[^@\s]+\.[^@\s]+[a-zA-Z])', r'Email: [\1](mailto:\1)', text)


def add_https_to_somelinks(text):
    www_links_without_https = r'([^https?://])(www)'
    if re.search(www_links_without_https, text):
        text = re.sub(www_links_without_https, r'\1https://\2', text)
    return text

def check_length_of_http_links(matchobj):
    http_link = matchobj.group(0)
    if len(http_link) <= 28:
        return 'Web: [%s](%s)'%(http_link, http_link)
        
    return truncate_http_links(http_link)
    

def truncate_http_links(link):
    tuple_of_link = urlparse(link)
    if len(tuple_of_link.netloc) >= 21:
        long_http_link_without_path = tuple_of_link.scheme + '://'+ tuple_of_link.netloc
        return 'Web: [%s...](%s)'%(long_http_link_without_path, link)
    else:
        truncated_http_link = link[:28]+'...'
        return 'Web: [%s](%s)'%( truncated_http_link, link)


def clean_text(text):
    text = clean_up_newlines(text)
    text = clean_up_http_links(text)
    text = clean_up_email_links(text)
    return text
