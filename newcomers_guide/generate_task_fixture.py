import json
from newcomers_guide.process_files import process_all_task_files


def generate_task_fixture(files):
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

    tasks = process_all_task_files(files)
    tasks_as_json = json.dumps(tasks, ensure_ascii=False, sort_keys=True, indent=4)

    json_lines = tasks_as_json.split('\n')
    json_lines_with_spaces = map(lambda line: 8*' ' + line, json_lines)
    joined_json_lines = '\n'.join(json_lines_with_spaces)

    return header + joined_json_lines + footer
