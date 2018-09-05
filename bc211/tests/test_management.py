from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

ONE_AGENCY_FIXTURE = 'bc211/data/BC211_data_one_agency.xml'
MULTI_AGENCY_FIXTURE = 'bc211/data/BC211_data_excerpt.xml'

class TestImportBc211Data(TestCase):
    def test_import_one_record(self):
        out = StringIO()
        call_command('import_bc211_data', ONE_AGENCY_FIXTURE, stdout=out)
        expected = ('Successfully imported 1 organization(s), '
                    '1 location(s), 1 service(s), '
                    '17 taxonomy term(s), 1 address(es), 2 phone number type(s), '
                    'and 2 phone number(s)')
        self.assertIn(expected, out.getvalue())

    def test_import_many_records(self):
        out = StringIO()
        call_command('import_bc211_data', MULTI_AGENCY_FIXTURE, stdout=out)
        expected = ('Successfully imported 16 organization(s), '
                    '40 location(s), 40 service(s), '
                    '134 taxonomy term(s), 32 address(es), 5 phone number type(s), '
                    'and 69 phone number(s)')
        self.assertIn(expected, out.getvalue())

    def test_import_invalid_file(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('import_bc211_data', 'NonExistentFile', stdout=out)
