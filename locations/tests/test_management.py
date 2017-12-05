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
        self.assertIn('Successfully imported 1 organization(s) and 1 location(s)',
                      out.getvalue())

    def test_import_many_records(self):
        out = StringIO()
        call_command('import_bc211_data', MULTI_AGENCY_FIXTURE, stdout=out)
        self.assertIn('Successfully imported 16 organization(s) and 40 location(s)',
                      out.getvalue())

    def test_import_invalid_file(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('import_bc211_data', 'NonExistentFile', stdout=out)
