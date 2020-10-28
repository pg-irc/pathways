import os
import logging
from .parser import parse_required_field, parse_optional_field, parse_website_with_prefix
from bc211.open_referral_csv_import import dtos
from human_services.services.models import Service

LOGGER = logging.getLogger(__name__)


def import_services_file(root_folder):
    filename = 'services.csv'
    path = os.path.join(root_folder, filename)
    try:
        with open(path, 'r') as file: 
            reader = csv.reader(file)
            headers = reader.__next__()
            for row in reader:
                if not row:
                    return
                service = parse_service(headers, row)
                save_service(service)
    except FileNotFoundError as error:
            LOGGER.error('Missing services.csv file.')
            raise


def parse_service(headers, row):
    service = {}
    service_id = row[0]
    organization_id = row[1]
    name = row[3]
    alternate_name = row[4]
    description = row[5]
    website = row[6]
    email = row[7]
    for header in headers:
        if header == 'id':
            service['id'] = parse_required_field('id', service_id)
        elif header == 'organization_id':
            service['organization_id'] = parse_required_field('organization_id', organization_id)
        elif header == 'name':
            service['name'] = parse_required_field('name', name)
        elif header == 'alternate_name':
            service['alternate_name'] = parse_optional_field('alternate_name', alternate_name)
        elif header == 'description':
            service['description'] = parse_optional_field('description', description)
        elif header == 'url':
            service['website'] = parse_website_with_prefix('website', website)
        elif header == 'email':
            service['email'] = parse_optional_field('email', email)
        else:
            continue
    return dtos.Service(id=service['id'], organization_id=service['organization_id'], name=service['name'],
                        alternate_name=service['alternate_name'], description=service['description'],
                        website=service['website'], email=service['email'])


def save_service(service):
    active_record = build_service_active_record(service)
    active_record.save()
    

def build_service_active_record(service):
    active_record = Service()
    active_record.id = service.id
    active_record.organization_id = service.organization_id
    return active_record