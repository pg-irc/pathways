import os
import logging
from bc211.parser import remove_double_escaped_html_markup

LOGGER = logging.getLogger(__name__)


def import_open_referral_files(root_folder):
    try:
        import_organizations_file(root_folder)
    except Exception as error:
        LOGGER.error(error)

    
def import_organizations_file(root_folder):
    filename = 'organizations.csv'
    path = os.path.join(root_folder, filename)
    try:
        with open(path, 'r') as file: 
            reader = csv.reader(file)
            headers = reader.__next__()
            for row in reader:
                if not row:
                    return
                organization = parse_organization(headers, row)
    except FileNotFoundError as error:
            LOGGER.error('Missing organizations.csv file.')
            raise


def parse_organization(headers, row):
    organization = {}
    organization_id = row[0]
    name = row[1]
    alternate_name = row[2]
    description = row[3]
    for header in headers:
        if header == 'id':
            organization['id'] = parse_required_field('id', organization_id)
        elif header == 'name':
            organization['name'] = parse_required_field('name', name)
        elif header == 'alternate_name':
            organization['alternate_name'] = parse_optional_field('alternate_name', alternate_name)
        elif header == 'description':
            organization['description'] = parse_optional_field('description', description)
        else:
            continue
    return organization


def parse_required_field(field, value):
    try:
        return remove_double_escaped_html_markup(value)
    except AttributeError:
        LOGGER.error('Missing required field: "{0}"'.format(field))
        raise


def parse_optional_field(field, value):
    if value is None:
        return None
    return remove_double_escaped_html_markup(value)