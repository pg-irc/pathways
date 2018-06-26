import os
import collections


def parse_file_path(path):
    parsed_file_path = collections.namedtuple('parsed_file_path',
                                              ['chapter', 'type', 'id', 'locale', 'title'])
    split_path = path.split(os.sep)
    length = len(split_path)
    if length < 5:
        raise Exception(path + ': path is too short')
    name = split_path[length-1]
    split_name = name.split('.')
    return parsed_file_path(chapter=split_path[length - 4],
                            type=split_path[length - 3],
                            id=split_path[length - 2],
                            title=split_name[1],
                            locale=split_name[0])
