import json


def generate_task_fixture(tasks):
    header = ('// intended to be located at pathways-frontend/src/fixtures/tasks.ts\n'
              '\n'
              'import { Store } from \'./types/tasks\';\n'
              'export { Id, Task, TaskUserSettings, TaskMap, TaskUserSettingsMap, TaskList, Store } from \'./types/tasks\';\n'
              '\n'
              'export const buildTasksFixture = (): Store => {\n'
              '    return {\n'
              '        taskMap: ')

    footer = ('\n'
              '    }\n'
              '}')

    tasks_as_json = json.dumps(tasks, ensure_ascii=False, sort_keys=True, indent=4)

    return header + add_leading_spaces(tasks_as_json) + footer


def generate_taxonomy_fixture(taxonomies):
    header = ''
    footer = ''
    taxonomies_as_json = json.dumps(taxonomies, ensure_ascii=False, sort_keys=True, indent=4)
    return header + add_leading_spaces(taxonomies_as_json) + footer


def add_leading_spaces(tasks_as_json):
    json_lines = tasks_as_json.split('\n')
    json_lines_with_spaces = map(lambda line: 8*' ' + line, json_lines)
    return '\n'.join(json_lines_with_spaces)
