import collections
from django.core import exceptions


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
