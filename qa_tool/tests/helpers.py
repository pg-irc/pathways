from qa_tool import models
from common.testhelpers.random_test_values import a_string, a_website_address, an_integer


class AlgorithmBuilder:
    def __init__(self):
        self.id = an_integer()
        self.name = a_string()
        self.url = a_website_address()
        self.notes = a_string()

    def build(self):
        result = models.Algorithm()
        result.id = self.id
        result.name = self.name
        result.url = self.url
        result.notes = self.notes
        return result

    def with_name(self, name):
        self.name = name
        return self

    def with_url(self, url):
        self.url = url
        return self

    def with_notes(self, notes):
        self.notes = notes
        return self
