from django.test import TestCase
from newcomers_guide.generate_task_fixture import generate_task_fixture


class GenerateFixtureTest(TestCase):
    def setUp(self):
        self.english_path = 'some/path/chapter/tasks/To_learn_english/en.Learn_english.txt'
        self.content = 'the content in English'

    def test_include_content_id_from_path(self):
        self.maxDiff = None
        result = generate_task_fixture([[self.english_path, self.content]])
        expected = ('// intended to be located at pathways-frontend/src/fixtures/tasks.ts\n'
                    '\n'
                    'import { Store } from \'./types/tasks\';\n'
                    'export { Id, Task, TaskUserSettings, TaskMap, TaskUserSettingsMap, TaskList, Store } from \'./types/tasks\';\n'
                    '\n'
                    'export const buildTasksFixture = (): Store => {\n'
                    '    return {\n'
                    '        taskMap: {\n'
                    '    "To_learn_english": {\n'
                    '        "description": {\n'
                    '            "en": "the content in English"\n'
                    '        },\n'
                    '        "id": "To_learn_english",\n'
                    '        "title": {\n'
                    '            "en": "Learn_english"\n'
                    '        }\n'
                    '    }\n'
                    '}\n'
                    '    }\n'
                    '}')
        self.assertEqual(result, expected)
