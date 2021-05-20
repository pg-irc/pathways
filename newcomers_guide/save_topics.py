import collections
from django.utils import translation
from search.models import Task
from bc211.import_icarol_xml.taxonomy import create_taxonomy_term_active_record


def save_topics(topics, counts):
    translation.activate('en')
    for _, topic in topics['taskMap'].items():
        record = Task()
        record.id = topic['id']
        record.name = topic['title']['en']
        record.description = topic['description']['en']
        record.save()

        for taxonomy_term in topic['taxonomyTerms']:
            taxonomy_term_record = get_or_create_taxonomy_term(taxonomy_term, counts)
            record.taxonomy_terms.add(taxonomy_term_record)

        record.save()


def get_or_create_taxonomy_term(taxonomy_term, counts):
    taxonomy_term_type = collections.namedtuple('taxonomy_term_type',
                                                ['taxonomy_id', 'name'])
    taxonomy_term = taxonomy_term_type(taxonomy_id=taxonomy_term['taxonomyId'],
                                       name=taxonomy_term['taxonomyTermId'])
    return create_taxonomy_term_active_record(taxonomy_term, counts)
