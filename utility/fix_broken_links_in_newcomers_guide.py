import os
import sys
import csv


def is_topic_file(path):
    sep = os.sep
    is_under_topics_folder = path.find(sep + 'topics' + sep) > 0
    is_mark_down = path.endswith('.md')
    return is_under_topics_folder and is_mark_down


def read_file_content(path):
    with open(path, 'r') as file:
        return file.read()


def write_file_content(path, content):
    with open(path, 'w') as file:
        return file.write(content)


def read_csv_data_from_file(csv_path):
    result = []
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            result.append(row)
    return result


fixed_links = sorted(
    read_csv_data_from_file(sys.argv[1]),
    key=lambda x: len(x[0]),
    reverse=True
)


def fix_link(content, bad_link, good_link):
    found = content.find(bad_link) != -1
    if found:
        content = content.replace(bad_link, good_link)
    return [found, content]


def strip_trailing_slash(url):
    while url.endswith('/'):
        url = url[:-1]
    return url


def fix_links_in_file(path):
    dirty = False
    content = read_file_content(path)
    for line in fixed_links:
        bad_link = strip_trailing_slash(line[0].strip())
        good_link = strip_trailing_slash(line[2].strip())

        if bad_link == '' or good_link == '' or good_link == 'OK':
            continue

        bad_link_with_http = bad_link.replace('https:', 'http:')
        bad_link_with_https = bad_link.replace('http:', 'https:')

        found1, content = fix_link(content, bad_link_with_http, good_link)
        found2, content = fix_link(content, bad_link_with_https, good_link)
        dirty = dirty or found1 or found2

    if dirty:
        write_file_content(path, content)


def main():
    folder = '../content/NewcomersGuide/'
    for root, _, filenames in os.walk(folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_topic_file(path):
                fix_links_in_file(path)


main()
