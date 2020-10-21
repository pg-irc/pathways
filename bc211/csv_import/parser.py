import csv
import re
import hashlib
import uuid


def parse(sink, lines):
    reader = csv.reader(lines.split('\n'))
    headers = reader.__next__()
    location_ids = {}
    phone_ids = {}
    taxonomy_term_ids = {}
    for row in reader:
        organization_or_service = {}
        is_organization = False
        parent_organization_id = None
        location = {}
        addresses = [{}, {}]
        phone_numbers = [{}]
        taxonomy_terms = []
        service_taxonomy_terms = []
        if not row:
            continue
        for header, value in zip(headers, row):
            organization_or_service = parse_organization_and_service_fields(header, value, organization_or_service)
            location = parse_locations_fields(header, value, location)
            addresses = parse_address_fields(header, value, addresses)
            phone_numbers = parse_phone_numbers(header, value, phone_numbers)
            if header == 'TaxonomyTerm':
                taxonomy_terms += parse_taxonomy_terms(value)
            if header == 'ParentAgencyNum':
                is_organization = value == '0'
                parent_organization_id = None if is_organization else value
        location['id'] = compute_location_id(location, addresses, phone_numbers)
        location['organization_id'] = organization_or_service['id'] if is_organization else parent_organization_id
        if location['id'] not in location_ids:
            sink.write_location(location)
            location_ids[location['id']] = 1
        if is_organization:
            sink.write_organization(organization_or_service)
        else:
            organization_or_service['organization_id'] = parent_organization_id
            for item in taxonomy_terms:
                the_id = compute_hash(organization_or_service['id'], item['id'])
                service_taxonomy_terms.append({'id': the_id,
                                               'service_id': organization_or_service['id'],
                                               'taxonomy_id': item['id'],
                                               'taxonomy_detail': '',
                                               })
            sink.write_service(organization_or_service, location['id'])
        for i, item in enumerate(addresses):
            if not addresses[i]:
                continue
            addresses[i]['id'] = str(uuid.uuid4())
            addresses[i]['location_id'] = location['id']
            sink.write_address(addresses[i])
        for i, item in enumerate(phone_numbers):
            the_id = compute_hash(item['number'])
            if not item['number'] or the_id in phone_ids:
                continue
            phone_ids[the_id] = 1
            item['id'] = the_id
            item['location_id'] = location['id']
            sink.write_phone_number(item)
        for item in taxonomy_terms:
            if item['id'] not in taxonomy_term_ids:
                sink.write_taxonomy_term(item)
                taxonomy_term_ids[item['id']] = 1
        sink.write_service_taxonomy_terms(service_taxonomy_terms)
    return sink


def parse_organization_and_service_fields(header, value, organization_or_service):
    output_header = organization_header_map.get(header, None)
    if output_header:
        organization_or_service[output_header] = value
    return organization_or_service


def parse_address_fields(header, value, addresses):
    output_address_header = address_header_map.get(get_normalized_address_header(header), None)
    is_physical_address_type = header.startswith('Physical')
    if output_address_header:
        index = 1 if is_physical_address_type else 0
        addresses[index][output_address_header] = value
        addresses[index]['type'] = 'physical_address' if is_physical_address_type else 'postal_address'
    return addresses


def parse_locations_fields(header, value, location):
    output_location_header = location_header_map.get(header, None)
    if output_location_header:
        if output_location_header in ['latitude', 'longitude']:
            try:
                value = float(value)
            except:
                value = None
        location[output_location_header] = value
    return location


def parse_phone_numbers(header, value, phone_numbers):
    output_phone_header = phone_header_map.get(phone_header_with_index_one(header), None)
    if output_phone_header:
        phone_index = get_zero_based_phone_index(header)
        while phone_index and len(phone_numbers) <= phone_index:
            phone_numbers.append({})
        phone_numbers[phone_index][output_phone_header] = value
    return phone_numbers


def compute_location_id(location, addresses, phone_numbers):
    return compute_hash(compute_address_id(addresses[0]),
                        compute_address_id(addresses[1]),
                        compute_phone_number_id(phone_numbers[0]),
                        str(location.get('latitude', '')),
                        str(location.get('longitude', ''))
                        )


def compute_address_id(address):
    return compute_hash(
        address.get('address_1', ''),
        address.get('address_2', ''),
        address.get('address_3', ''),
        address.get('address_4', ''),
        address.get('city', ''),
        address.get('state_province', ''),
        address.get('postal_code', ''),
        address.get('country', ''),
        )


def compute_phone_number_id(phone_number):
    if not phone_number:
        return ''
    return compute_hash(phone_number.get('number', ''))


def compute_hash(*args):
    hasher = hashlib.sha1()
    for arg in args:
        hasher.update(arg.encode('utf-8'))
    return hasher.hexdigest()


organization_header_map = {
    'ResourceAgencyNum': 'id',
    'PublicName': 'name',
    'AgencyDescription': 'description',
    'AlternateName': 'alternate_name',
    'EmailAddressMain': 'email',
    'WebsiteAddress': 'url',
}


location_header_map = {
    'ResourceAgencyNum': 'organization_id',
    'PublicName': 'name',
    'AlternateName': 'alternate_name',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
}


address_header_map = {
    'MailingAddress1': 'address_1',
    'MailingAddress2': 'address_2',
    'MailingAddress3': 'address_3',
    'MailingAddress4': 'address_4',
    'MailingCity': 'city',
    'MailingStateProvince': 'state_province',
    'MailingPostalCode': 'postal_code',
    'MailingCountry': 'country',
}


def get_normalized_address_header(fff):
    return re.sub(r'^Physical', 'Mailing', fff)


def phone_header_with_index_one(phone_field_with_any_index):
    return re.sub(r'^Phone\d', 'Phone1', phone_field_with_any_index)


def get_zero_based_phone_index(phone):
    r = re.match(r'^Phone(\d)', phone)
    return int(r[1]) - 1 if r else None


phone_header_map = {
    'Phone1Number': 'number',
    'Phone1Type': 'type',
    'Phone1Name': 'description',  # there is also a field Phone1Description but BC211 does not appear to use it
}


def parse_taxonomy_terms(value):
    names = re.split(r'[;\-\* ]', value)
    return [{'id': compute_hash(name, 'bc211'),
             'name': name,
             'vocabulary': 'bc211',
             'parent_name': '',
             'parent_id': ''} for name in names if name]
