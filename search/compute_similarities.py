import spacy
import sklearn.preprocessing
from textacy.vsm import Vectorizer
from django.utils.text import slugify
import re


def to_topic_ids_and_descriptions(topics):
    ids = []
    descriptions = []
    for _, topic in topics['taskMap'].items():
        ids.append(slugify(topic['id']))
        english_description = topic['title']['en'] + ' ' + topic['description']['en']
        descriptions.append(english_description)
    return (ids, descriptions)


def to_service_ids_and_descriptions(services):
    ids = []
    descriptions = []
    for service in services:
        ids.append(service.id)
        description_without_phone_numbers = remove_phone_numbers(service.description) or ''
        descriptions.append(service.name + ' ' + description_without_phone_numbers)
    return (ids, descriptions)


def compute_similarities(docs):
    nlp = spacy.load('en')
    spacy_docs = [nlp(doc) for doc in docs]
    tokenized_docs = ([tok.lemma_ for tok in doc] for doc in spacy_docs)
    # tf-idf
    vectorizer = Vectorizer(tf_type='linear', apply_idf=True, idf_type='smooth', apply_dl=False)
    term_matrix = vectorizer.fit_transform(tokenized_docs)
    return compute_cosine_doc_similarities(term_matrix)


def compute_cosine_doc_similarities(matrix):
    normalized_matrix = sklearn.preprocessing.normalize(matrix, axis=1)
    return normalized_matrix * normalized_matrix.T


def remove_phone_numbers(description):
    if not description:
        return None
    return re.sub(r'(\+?[0-9]{1,2}-|\+?[\(\)\d]{3,5}-\d{3}-\d{4})', '', description)
