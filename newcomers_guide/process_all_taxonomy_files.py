import collections
from django.core import exceptions
from newcomers_guide.parse_file_path import parse_file_path


class TaxonomyTermReference:
    def __init__(self, taxonomy_id, taxonomy_term_id, content_type, content_id):
        self.taxonomy_id = taxonomy_id
        self.taxonomy_term_id = taxonomy_term_id
        self.content_type = content_type
        self.content_id = content_id


def process_all_taxonomy_files(file_specs):
    result = []
    for spec in file_specs:
        path = spec[0]
        file_content = spec[1]
        parsed_path = parse_file_path(path)
        content_id = parsed_path.id
        content_type = parsed_path.type
        parsed_terms = parse_taxonomy_file(file_content)
        for term in parsed_terms:
            result.append(TaxonomyTermReference(taxonomy_id=term.taxonomy_id,
                                                taxonomy_term_id=term.taxonomy_term_id,
                                                content_type=content_type,
                                                content_id=content_id))
    return result


def parse_taxonomy_file(taxonomy_terms):
    taxonomy_term_type = collections.namedtuple('taxonomy_term_type',
                                                ['taxonomy_id', 'taxonomy_term_id'])
    result = []
    items = taxonomy_terms.split(',')
    for item in items:
        validate_item(item)
        split_point = item.find(':')
        result.append(taxonomy_term_type(taxonomy_id=item[:split_point].strip(),
                                         taxonomy_term_id=item[split_point+1:].strip()))
    return result


def validate_item(item):
    if item.find(' :') != -1 or item.find(': ') != -1:
        raise exceptions.ValidationError('"' + item + '" : Invalid taxonomy term format')
