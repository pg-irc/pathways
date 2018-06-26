import json


class TaskBuilder:
    def __init__(self):
        self.task = {}

    def get_id(self):
        return self.task['id']

    def set_id(self, the_id):
        self.task['id'] = the_id
        return self

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
