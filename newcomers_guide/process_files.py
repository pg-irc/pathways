from newcomers_guide.parse_file_path import parse_file_path
from newcomers_guide.task_builder import TaskBuilder
from newcomers_guide.data_cleanup import clean_up_links, clean_up_newlines


def process_all_task_files(file_specs):
    builders = {}
    for spec in file_specs:
        path = spec[0]
        description = clean_text(spec[1])

        parsed_path = parse_file_path(path)
        task_id = parsed_path.id

        if parsed_path.type == 'tasks':
            ensure_builder_exists_for_task(builders, task_id)
            add_properties_for_locale(builders[task_id], parsed_path, description)

    return make_task_map(builders)


def clean_text(text):
    text = clean_up_newlines(text)
    text = clean_up_links(text)
    return text


def ensure_builder_exists_for_task(builders, task_id):
    if task_id not in builders:
        builders[task_id] = TaskBuilder()
        builders[task_id].set_id(task_id)


def add_properties_for_locale(builder, parsed_path, description):
    locale = parsed_path.locale
    builder.set_title_in_locale(locale, parsed_path.title)
    builder.set_description_in_locale(locale, description)


def make_task_map(builders):
    tasks = {}
    for key in builders:
        tasks[key] = builders[key].to_task()
    return tasks
