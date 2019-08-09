import re
import logging
import spacy
import sklearn.preprocessing
from textacy.vsm import Vectorizer
from django.utils.text import slugify
from spacy.lang.en.stop_words import STOP_WORDS as SPACY_STOP_WORDS

LOGGER = logging.getLogger(__file__)


def to_topic_ids_and_descriptions(topics):
    ids = []
    descriptions = []
    i = 0
    for _, topic in topics['taskMap'].items():
        ids.append(slugify(topic['id']))
        english_description = topic['title']['en'] + ' ' + topic['description']['en']
        descriptions.append(english_description)
        i = i + 1
        if i == 10:
            return (ids, descriptions)
    return (ids, descriptions)


def to_service_ids_and_descriptions(services):
    ids = []
    descriptions = []
    for service in services:
        ids.append(service.id)
        description_without_phone_numbers = remove_phone_numbers(service.description) or ''
        descriptions.append(service.name + ' ' + description_without_phone_numbers)
    return (ids, descriptions)


def compute_similarities_by_tf_idf(docs, topic_ids, service_ids, results_to_save, results_file):
    if is_saving_intermediates_to_file(results_to_save, results_file):
        return compute_similarities_and_save_intermediates(docs, topic_ids, service_ids,
                                                           results_to_save, results_file)

    return compute_similarities(docs)


def is_saving_intermediates_to_file(results_to_save, results_file):
    if results_to_save > 0 and results_file:
        return True

    if results_to_save > 0 and not results_file:
        message = 'Output file (--results_file) was not specified for intermediary results'
        raise RuntimeError(message)

    if results_to_save <= 0 and results_file:
        message = ('Output file was specified (--results_file) ' +
                   'but zero results are being saved (--save_intermediate_results)')
        raise RuntimeError(message)

    return False


def compute_similarities(docs):
    vectorizer = Vectorizer(tf_type='linear', apply_idf=True, idf_type='smooth', apply_dl=False)
    term_matrix = compute_term_matrix(vectorizer, docs)
    return compute_cosine_doc_similarities(term_matrix)


def compute_similarities_and_save_intermediates(docs, topic_ids, service_ids, results_to_save, results_file):
    vectorizer = Vectorizer(tf_type='linear', apply_idf=True, idf_type='smooth', apply_dl=False)
    term_matrix = compute_term_matrix(vectorizer, docs)
    write_intermediary_results_as_csv(vectorizer, term_matrix, topic_ids,
                                      service_ids, results_to_save, results_file)
    return compute_cosine_doc_similarities(term_matrix)


def compute_term_matrix(vectorizer, docs):
    nlp = spacy.load('en')
    spacy_docs = [nlp(doc) for doc in docs]
    tokenized_docs = ([token.lemma_.lower() for token in doc if not is_stop_word(token)] for doc in spacy_docs)
    return vectorizer.fit_transform(tokenized_docs)


def is_stop_word(token):
    return (token.is_space or
            token.is_punct or
            token.is_bracket or
            token.like_num or
            # token.like_url or
            # token.like_email or
            token.lemma_.lower() in STOPLIST)


def stop_list_all_lower_case():
    stop_words = '''
    and/or $
    Monday Tuesday Wednesday Thursday Friday Saturday Sunday Mon Tue Wed Thu Fri Sat Sun
    '''
    stop_words = set(stop_words.split()).union(SPACY_STOP_WORDS)
    return {word.lower() for word in stop_words}


STOPLIST = stop_list_all_lower_case()


def write_intermediary_results_as_csv(vectorizer, term_matrix, topic_ids, service_ids, results_to_save, file_handle):
    document_index = 0
    score_matrix = term_matrix.toarray()
    document_ids = topic_ids + service_ids
    for document_id in document_ids[0:results_to_save]:
        write_intermediary_results_for_document(file_handle, vectorizer, score_matrix, document_index, document_id)
        document_index += 1
    file_handle.close()


def write_intermediary_results_for_document(file_handle, vectorizer, score_matrix, document_index, document_id):
    file_handle.write('"')
    file_handle.write(document_id)
    file_handle.write('"')
    write_terms_sorted_by_scores(file_handle, vectorizer, score_matrix, document_index)
    file_handle.write('\n')


def write_terms_sorted_by_scores(file_handle, vectorizer, score_matrix, document_index):
    terms_with_scores = get_document_terms(vectorizer, score_matrix, document_index)
    terms_sorted_by_score = sorted(terms_with_scores, key=lambda term: term[1], reverse=True)
    write_comma_separated_terms_with_scores(file_handle, terms_sorted_by_score)


def get_document_terms(vectorizer, score_matrix, document_index):
    document_terms = []
    for term_index in range(len(vectorizer.terms_list)):
        score = score_matrix[document_index][term_index]
        if score > 0:
            term = vectorizer.terms_list[term_index]
            document_terms.append((term, score))
    return document_terms


def write_comma_separated_terms_with_scores(file_handle, document_terms):
    for term_with_score in document_terms:
        term = term_with_score[0]
        score = term_with_score[1]

        file_handle.write(',"')
        file_handle.write(term)
        file_handle.write('(')
        file_handle.write('%.2f' % score)
        file_handle.write(')"')


def compute_cosine_doc_similarities(matrix):
    normalized_matrix = sklearn.preprocessing.normalize(matrix, axis=1)
    return normalized_matrix * normalized_matrix.T


def remove_phone_numbers(description):
    if not description:
        return None
    return re.sub(r'(\+?[0-9]{1,2}-|\+?[\(\)\d]{3,5}-\d{3}-\d{4})', '', description)
