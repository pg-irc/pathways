import os
from newcomers_guide import exceptions
from glob import glob


def read_topic_data(root_folder):
    task_data = []
    for root, _, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_topic_file(path):
                task_data.append([path, read_file_content(path)])
    return task_data


def read_taxonomy_data(root_folder):
    validate_taxonomy_data(root_folder)

    taxonomy_data = []
    for root, _, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            path = os.path.join(root, filename)
            if is_taxonomy_file(path):
                taxonomy_data.append([path, read_file_content(path)])
    return taxonomy_data


def read_file_content(path):
    with open(path, 'r') as file:
        try:
            content = file.read()
            return content
        except ValueError as error:
            raise exceptions.DecodeError(path)


def is_topic_file(path):
    sep = os.sep
    return path.find(sep + 'topics' + sep) > 0 and is_content_file(path)


def is_content_file(path):
    return path.endswith('.md')


def is_taxonomy_file(path):
    sep = os.sep
    return path.endswith(sep + 'taxonomy.txt')


def validate_taxonomy_data(root_folder):
    invalid_folders = get_topic_folders_without_taxonomy_files(root_folder)
    if not invalid_folders:
        return
    folder_names = ', '.join(invalid_folders)
    raise Exception(f'There is a taxonomy file missing in these topic folders:{folder_names}')


def get_topic_folders_without_taxonomy_files(root_folder):
    folders = get_paths_to_topic_folders(root_folder)
    return [f for f in folders if is_taxonomy_file_missing(f)]


def is_taxonomy_file_missing(path):
    return not os.path.isfile(path + '/taxonomy.txt')


def get_paths_to_topic_folders(root_folder):
    return glob(root_folder + '/*/topics/*/')
