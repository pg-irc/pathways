from django.core.management import CommandError, call_command
from django.test import TestCase

from human_services.organizations.tests.helpers import OrganizationBuilder
from translation.tests.helpers import add_base_translation, add_translation
from tempfile import NamedTemporaryFile, TemporaryDirectory
import io
import os
import polib

TEST_PARLER_PO_CONTACT = 'test_content_translation_import@example.com'

class ContentTranslationToolsImportCommandTests(TestCase):
    def test_requires_directory_argument(self):
        with self.assertRaisesRegex(CommandError, 'Error: the following arguments are required: file'):
            call_command('content_translation_import')

class ContentTranslationToolsImportTestsWithBaseTranslations(TestCase):
    def setUp(self):
        organization_1 = OrganizationBuilder().with_id('one').build()
        add_base_translation(
            organization_1, name='organization_one_translation_name_msgid', description=''
        )
        add_translation(
            organization_1, 'fr', name='organization_one_translation_name_msgstr_fr'
        )

        organization_2 = OrganizationBuilder().with_id('two').build()
        add_base_translation(
            organization_2, name='', description='organization_two_translation_description_msgid'
        )
        add_translation(
            organization_2, 'fr', description='organization_two_translation_description_msgstr_fr'
        )

        organization_3 = OrganizationBuilder().with_id('three').build()
        add_base_translation(
            organization_3, name='organization_three_translation_name_msgid', description='organization_three_translation_description_msgid'
        )

        self.translatable_objects = [
            organization_1,
            organization_2,
            organization_3
        ]

        self.out_dir = TemporaryDirectory()

    def test_import_po_file_with_no_language_reports_error(self):
        po_file = polib.POFile()

        po_file_path = os.path.join(self.out_dir.name, 'organizations.organization.po')
        po_file.save(po_file_path)

        stdout, stderr = _run_content_translation_import(po_file_path)

        self.assertIn('Skipping file: No language metadata', stderr.getvalue())

    def test_import_po_file_keeps_existing_translations(self):
        self._import_po_entries('fr', [])

        master = self.translatable_objects[0]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_one_translation_name_msgstr_fr')
        self.assertEqual(translation.description, None)

        master = self.translatable_objects[1]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, '')
        self.assertEqual(translation.description, 'organization_two_translation_description_msgstr_fr')

        master = self.translatable_objects[2]
        with self.assertRaises(master.translations.model.DoesNotExist):
            master.get_translation('fr')
            translation.refresh_from_db()

    def test_import_po_file_with_updated_translation(self):
        self._import_po_entries('fr', [
            polib.POEntry(
                occurrences=[('organizations.organization@name@one', '')],
                msgid='organization_one_translation_name_msgid',
                msgstr='organization_one_translation_name_msgstr_fr_2'
            )
        ])

        master = self.translatable_objects[0]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_one_translation_name_msgstr_fr_2')

    def test_import_po_file_with_new_translation_entry(self):
        self._import_po_entries('fr', [
            polib.POEntry(
                occurrences=[('organizations.organization@name@three', '')],
                msgid='organization_three_translation_name_msgid',
                msgstr='organization_three_translation_name_msgstr_fr'
            )
        ])

        master = self.translatable_objects[0]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_one_translation_name_msgstr_fr')
        self.assertEqual(translation.description, None)

        master = self.translatable_objects[1]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, '')
        self.assertEqual(translation.description, 'organization_two_translation_description_msgstr_fr')

        master = self.translatable_objects[2]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_three_translation_name_msgstr_fr')
        self.assertEqual(translation.description, None)

    def test_import_po_file_with_new_language(self):
        self._import_po_entries('es', [
            polib.POEntry(
                occurrences=[('organizations.organization@name@one', '')],
                msgid='organization_one_translation_name_msgid',
                msgstr='organization_one_translation_name_msgstr_es'
            )
        ])

        master = self.translatable_objects[0]
        translation = master.get_translation('es')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_one_translation_name_msgstr_es')
        self.assertEqual(translation.description, None)

        master = self.translatable_objects[1]
        with self.assertRaises(master.translations.model.DoesNotExist):
            master.get_translation('es')

        master = self.translatable_objects[2]
        with self.assertRaises(master.translations.model.DoesNotExist):
            master.get_translation('es')

    def test_import_po_file_with_invalid_msgids(self):
        self._import_po_entries('fr', [
            polib.POEntry(
                occurrences=[('organizations.organization@name@one', '')],
                msgid='not_the_msgid',
                msgstr='should_not_be_set'
            )
        ])

        master = self.translatable_objects[0]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, 'organization_one_translation_name_msgstr_fr')
        self.assertEqual(translation.description, None)

    def test_import_po_file_skips_errors(self):
        self._import_po_entries('fr', [
            polib.POEntry(
                occurrences=[('organizations.organization@name@one', '')],
                msgid='not_the_msgid',
                msgstr='should_not_be_set'
            ),
            polib.POEntry(
                occurrences=[('not_a_field_id', '')],
                msgid='not_the_msgid',
                msgstr='should_not_be_set'
            ),
            polib.POEntry(
                occurrences=[('organizations.organization@description@two', '')],
                msgid='organization_two_translation_description_msgid',
                msgstr='organization_two_translation_description_msgstr_fr_2'
            )
        ])

        master = self.translatable_objects[1]
        translation = master.get_translation('fr')
        translation.refresh_from_db()
        self.assertEqual(translation.name, '')
        self.assertEqual(translation.description, 'organization_two_translation_description_msgstr_fr_2')

    def _import_po_entries(self, language, po_entries):
        po_file = polib.POFile()
        po_file.metadata['Language'] = language

        for po_entry in po_entries:
            po_file.append(po_entry)

        po_file_path = os.path.join(self.out_dir.name, 'organizations.organization.po')
        po_file.save(po_file_path)

        return _run_content_translation_import(po_file_path)

def _run_content_translation_import(*args, **kwargs):
    stdout = io.StringIO()
    stderr = io.StringIO()
    call_command('content_translation_import', *args, **kwargs, stdout=stdout, stderr=stderr)
    return stdout, stderr
