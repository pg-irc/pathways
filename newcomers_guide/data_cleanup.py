import re


def clean_up_newlines(text):
    single_newline = r'\b[ \t\r]*\n[ \t\r]*\b'
    text = re.sub(single_newline, ' ', text)

    double_newline = r'\b[ \t\r]*\n([ \t\r]*\n)+[ \t\r]*\b'
    text = re.sub(double_newline, '\n', text)
    return text


def clean_up_links(text):
    return re.sub(r'(https?://([a-zA-Z0-9\.\:]+)(/\S*)?)', r'[\2](\1)', text)
