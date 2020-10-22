import random
import copy
from common.testhelpers.random_test_values import an_integer


class Bc211CsvDataBuilder:
    def __init__(self):
        self.data = [self.a_row()]

    def a_row(self):
        row = {}
        row['ResourceAgencyNum'] = ''
        row['PublicName'] = ''
        row['AlternateName'] = ''
        row['AgencyDescription'] = ''
        row['EmailAddressMain'] = ''
        row['WebsiteAddress'] = ''
        row['Phone1Number'] = ''
        row['Phone1Type'] = ''
        return row

    def next_row(self):
        self.data.append(self.a_row())
        return self

    def duplicate_last_row(self):
        the_copy = copy.deepcopy(self.data[-1])
        self.data.append(the_copy)
        return self

    def with_field(self, key, value):
        self.data[-1][key] = value
        return self

    def as_organization(self):
        self.data[-1]['ParentAgencyNum'] = '0'
        return self

    def as_service(self):
        self.data[-1]['ParentAgencyNum'] = str(an_integer(min=1))
        return self

    def build(self):
        result = []
        shuffled_keys = list(self.data[0].keys())
        random.shuffle(shuffled_keys)
        line = ''
        for key in shuffled_keys:
            line += key + ','
        result.append(line)
        for row in self.data:
            line = ''
            for key in shuffled_keys:
                value = row.get(key, '')
                line += value + ','
            result.append(line)
        return result
