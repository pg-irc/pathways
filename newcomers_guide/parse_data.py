import os
import json
import collections
from django.core import exceptions
from django.utils.text import slugify
from newcomers_guide.clean_data import clean_text
from newcomers_guide.system_data import get_system_taxonomies, get_explore_taxonomy_id
from newcomers_guide.exceptions import TaxonomyError, ParseError
from search.models import TaskSimilarityScore


def parse_topic_files(file_specs):
    builders = {}
    for spec in file_specs:
        path = spec[0]
        description = clean_text(spec[1])

        parsed_path = parse_file_path(path)
        topic_id = parsed_path.id

        if parsed_path.type == 'topics':
            ensure_builder_exists_for_topic(builders, topic_id)
            add_properties_for_locale(builders[topic_id], parsed_path, description)

    return make_topic_map(builders)


def parse_file_path(path):
    parsed_file_path = collections.namedtuple('parsed_file_path',
                                              ['region', 'chapter', 'type', 'id', 'locale', 'title'])
    split_path = path.split(os.sep)
    length = len(split_path)
    if length < 5:
        raise exceptions.ValidationError(path + ': path is too short')
    name = split_path[length-1]
    validate_filename(name, path)
    title = get_title_from_file_name(name)
    locale = get_locale_from_file_name(name)
    topic_id = slugify(split_path[length - 2])
    return parsed_file_path(region=split_path[length - 5],
                            chapter=split_path[length - 4],
                            type=split_path[length - 3],
                            id=topic_id,
                            title=title,
                            locale=locale)


def validate_filename(file_name, path):
    first, last = find_periods_in_filename(file_name)

    file_extension = file_name[last+1:]
    if not is_content_file(file_extension):
        return

    too_few_periods = first == last
    no_language_code = first == 0
    no_article_name = first + 1 == last
    no_file_extension = last == len(file_name) - 1

    if (too_few_periods or no_language_code or no_article_name or no_file_extension):
        raise_invalid_filename_error(path)


def find_periods_in_filename(file_name):
    first = file_name.find('.')
    last = file_name.rfind('.')
    return first, last


def is_content_file(file_extension):
    content_file_extension = 'md'
    return file_extension == content_file_extension


def raise_invalid_filename_error(path):
    message = ': Invalid file name, should be <language code>.<article name>.md'
    raise exceptions.ValidationError(path + message)


def get_title_from_file_name(file_name):
    first, last = find_periods_in_filename(file_name)
    return file_name[first + 1:last]


def get_locale_from_file_name(file_name):
    return file_name.split('.')[0]


def ensure_builder_exists_for_topic(builders, topic_id):
    if topic_id not in builders:
        builders[topic_id] = create_topic_builder(topic_id)


def create_topic_builder(topic_id):
    builder = TopicBuilder()
    builder.set_id(topic_id)
    builder.set_related_topics(find_related_topics(topic_id))
    return builder


def find_related_topics(topic_id):
    related_topics = TaskSimilarityScore.objects.filter(first_task_id=topic_id).order_by('-similarity_score')
    return [topic.second_task_id for topic in related_topics]


class TopicBuilder:
    def __init__(self):
        self.topic = {
            'relatedTopics': [],
            'isNewlyRecommended': False
        }

    def get_id(self):
        return self.topic['id']

    def set_id(self, the_id):
        self.topic['id'] = the_id
        return self

    def set_region(self, region):
        self.topic['region'] = region
        return self

    def set_related_topics(self, related_topics):
        self.topic['relatedTopics'] = related_topics
        return self

    def set_chapter(self, chapter):
        self.topic['chapter'] = chapter
        return self

    def get_chapter(self):
        if 'chapter' not in self.topic:
            return None
        return self.topic['chapter']

    def set_title_in_locale(self, locale, title):
        self.ensure_key_exist('title')
        self.topic['title'][locale] = title
        return self

    def set_description_in_locale(self, locale, description):
        self.ensure_key_exist('description')
        self.topic['description'][locale] = description
        return self

    def ensure_key_exist(self, key):
        if key not in self.topic:
            self.topic[key] = {}

    def to_topic(self):
        return self.topic

    def to_json(self):
        return json.dumps(self.topic)


def make_topic_map(builders):
    topics = {}
    for key in builders:
        topics[key] = builders[key].to_topic()
    return {
        'taskMap': topics,
    }


def add_properties_for_locale(builder, parsed_path, description):
    region = parsed_path.region
    locale = parsed_path.locale
    chapter = parsed_path.chapter
    builder_chapter = builder.get_chapter()
    if builder_chapter and builder_chapter != chapter:
        message = parsed_path.id + ': don\'t use the same topic id in different chapters'
        raise exceptions.ValidationError(message)
    builder.set_chapter(chapter)
    builder.set_title_in_locale(locale, parsed_path.title)
    builder.set_description_in_locale(locale, description)
    builder.set_region(region)


def parse_taxonomy_files(file_specs):
    result = []
    for spec in file_specs:
        path = spec[0]
        file_content = spec[1]
        parsed_path = parse_file_path(path)
        content_id = parsed_path.id
        content_type = parsed_path.type
        try:
            parsed_terms = parse_taxonomy_terms(file_content)
        except:
            message = '{}: Failed to parse taxonomy file with content "{}"'.format(path, file_content)
            raise ParseError(message)

        for term in parsed_terms:
            validate_taxonomy_term(term, path)
            result.append(TaxonomyTermReference(taxonomy_id=term.taxonomy_id,
                                                taxonomy_term_id=term.taxonomy_term_id,
                                                content_type=content_type,
                                                content_id=content_id))
    return result


def validate_taxonomy_term(term, path):
    explore = get_explore_taxonomy_id()
    explore_taxonomy = get_system_taxonomies()[explore]

    if term.taxonomy_id == explore and term.taxonomy_term_id not in explore_taxonomy:
        message = '{}: Invalid explore taxonomy term "{}"'.format(path, term.taxonomy_term_id)
        raise TaxonomyError(message)


class TaxonomyTermReference:
    def __init__(self, taxonomy_id, taxonomy_term_id, content_type, content_id):
        self.taxonomy_id = taxonomy_id
        self.taxonomy_term_id = taxonomy_term_id
        self.content_type = content_type
        self.content_id = content_id


def parse_taxonomy_terms(taxonomy_terms):
    taxonomy_term_type = collections.namedtuple('taxonomy_term_type',
                                                ['taxonomy_id', 'taxonomy_term_id'])
    result = []
    items = taxonomy_terms.split(',')
    for item in items:
        validate_taxonomy_item(item)
        split_item = item.split(':')
        result.append(taxonomy_term_type(taxonomy_id=split_item[0].strip(),
                                         taxonomy_term_id=split_item[1].strip()))
    return result


def validate_taxonomy_item(item):
    if item.find(' :') != -1 or item.find(': ') != -1:
        raise exceptions.ValidationError('"' + item + '" : Invalid taxonomy term format')
