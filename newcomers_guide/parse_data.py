import os
import json
import collections
from django.core import exceptions
from django.utils.text import slugify
from newcomers_guide.clean_data import clean_text
from newcomers_guide.system_data import get_system_taxonomies, get_explore_taxonomy_id
from newcomers_guide.exceptions import TaxonomyError, ParseError
from search.models import TaskSimilarityScore


def parse_task_files(file_specs):
    builders = {}
    for spec in file_specs:
        path = spec[0]
        description = clean_text(spec[1])

        parsed_path = parse_file_path(path)
        task_id = parsed_path.id

        if parsed_path.type == 'tasks' or parsed_path.type == 'articles':
            ensure_builder_exists_for_task(builders, task_id)
            add_properties_for_locale(builders[task_id], parsed_path, description)

    return make_task_map(builders)


def parse_file_path(path):
    parsed_file_path = collections.namedtuple('parsed_file_path',
                                              ['chapter', 'type', 'id', 'locale', 'title'])
    split_path = path.split(os.sep)
    length = len(split_path)
    if length < 5:
        raise exceptions.ValidationError(path + ': path is too short')
    name = split_path[length-1]
    validate_filename(name)
    title = get_title_from_file_name(name)
    locale = get_locale_from_file_name(name)
    task_id = slugify(split_path[length - 2])
    return parsed_file_path(chapter=split_path[length - 4],
                            type=split_path[length - 3],
                            id=task_id,
                            title=title,
                            locale=locale)


def validate_filename(file_name):
    first, last = find_periods_in_filename(file_name)

    file_extension = file_name[last+1:]
    if not is_content_file(file_extension):
        return

    too_few_periods = first == last
    no_language_code = first == 0
    no_article_name = first + 1 == last
    no_file_extension = last == len(file_name) - 1

    if (too_few_periods or no_language_code or no_article_name or no_file_extension):
        raise_invalid_filename_error(file_name)


def find_periods_in_filename(file_name):
    first = file_name.find('.')
    last = file_name.rfind('.')
    return first, last


def is_content_file(file_extension):
    content_file_extension = 'md'
    return file_extension == content_file_extension


def raise_invalid_filename_error(file_name):
    message = ': Invalid file name, should be <language code>.<article name>.md'
    raise exceptions.ValidationError(file_name + message)


def get_title_from_file_name(file_name):
    first, last = find_periods_in_filename(file_name)
    return file_name[first + 1:last]


def get_locale_from_file_name(file_name):
    return file_name.split('.')[0]


def ensure_builder_exists_for_task(builders, task_id):
    if task_id not in builders:
        builders[task_id] = create_task_builder(task_id)


def create_task_builder(task_id):
    builder = TaskBuilder()
    builder.set_id(task_id)
    builder.set_related_tasks(find_related_tasks(task_id))
    return builder


def find_related_tasks(task_id):
    related_tasks = TaskSimilarityScore.objects.filter(first_task_id=task_id).order_by('-similarity_score')
    return [task.second_task_id for task in related_tasks]


class TaskBuilder:
    def __init__(self):
        self.task = {
            'relatedTasks': [],
            'completed': False
        }

    def get_id(self):
        return self.task['id']

    def set_id(self, the_id):
        self.task['id'] = the_id
        return self

    def set_related_tasks(self, related_tasks):
        self.task['relatedTasks'] = related_tasks
        return self

    def set_chapter(self, chapter):
        self.task['chapter'] = chapter
        return self

    def get_chapter(self):
        if 'chapter' not in self.task:
            return None
        return self.task['chapter']

    def set_title_in_locale(self, locale, title):
        self.ensure_key_exist('title')
        self.task['title'][locale] = title
        return self

    def set_description_in_locale(self, locale, description):
        self.ensure_key_exist('description')
        self.task['description'][locale] = description
        return self

    def ensure_key_exist(self, key):
        if key not in self.task:
            self.task[key] = {}

    def to_task(self):
        return self.task

    def to_json(self):
        return json.dumps(self.task)


def make_task_map(builders):
    tasks = {}
    for key in builders:
        tasks[key] = builders[key].to_task()
    return {
        'taskMap': tasks,
    }


def add_properties_for_locale(builder, parsed_path, description):
    locale = parsed_path.locale
    chapter = parsed_path.chapter
    builder_chapter = builder.get_chapter()
    if builder_chapter and builder_chapter != chapter:
        message = parsed_path.id + ': don\'t use the same task id in different chapters'
        raise exceptions.ValidationError(message)
    builder.set_chapter(chapter)
    builder.set_title_in_locale(locale, parsed_path.title)
    builder.set_description_in_locale(locale, description)


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
