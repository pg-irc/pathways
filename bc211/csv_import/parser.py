import csv
import re
import hashlib
import uuid
import datetime


class CsvMissingIdParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def parse(sink, lines, vocabulary=None):
    reader = csv.reader(lines)
    headers = reader.__next__()
    unique_location_ids = {}
    unique_phone_ids = {}
    unique_taxonomy_term_ids = {}
    line = 0

    for row in reader:
        line += 1
        if not row:
            continue

        organization_or_service = {}
        location = {}
        addresses = [{}, {}]
        phone_numbers = [{}]
        taxonomy_terms = []
        service_taxonomy_terms = []
        parent_id = None

        for header, value in zip(headers, row):
            parse_row(header, value, organization_or_service, location,
                      addresses, phone_numbers, taxonomy_terms, vocabulary)
            if header == 'ParentAgencyNum':
                parent_id = value

        if not organization_or_service['id']:
            raise CsvMissingIdParseException(f'Missing service or organization id at line {line}')

        set_location_ids(location, addresses, phone_numbers, organization_or_service['id'], parent_id)
        write_location_to_sink(location, unique_location_ids, sink)

        if parent_id == '0':
            sink.write_organization(organization_or_service)
        else:
            organization_or_service['organization_id'] = parent_id
            sink.write_service(organization_or_service, location['id'])
            compile_taxonomy_terms(taxonomy_terms, organization_or_service['id'], service_taxonomy_terms)

        write_to_sink(addresses, location['id'],
                      phone_numbers, unique_phone_ids,
                      taxonomy_terms, unique_taxonomy_term_ids,
                      service_taxonomy_terms, sink)
    return sink


def parse_row(header, value, organization_or_service, location, addresses, phone_numbers, taxonomy_terms, vocabulary):
    parse_organization_and_service_fields(header, value, organization_or_service)
    parse_locations_fields(header, value, location)
    parse_address_fields(header, value, addresses)
    parse_phone_number_fields(header, value, phone_numbers)
    parse_taxonomy_fields(header, value, taxonomy_terms, vocabulary)


def parse_organization_and_service_fields(header, value, organization_or_service):
    output_header = organization_header_map.get(header, None)
    if output_header:
        if output_header == 'last_verified_on-x':
            organization_or_service[output_header] = fix_date_time_string_if_exists(value)
        else:
            organization_or_service[output_header] = value


def fix_date_time_string_if_exists(date_time_string):
    if not date_time_string:
        return None
    date_string = date_time_string.split()[0]
    date = datetime.datetime.strptime(date_string, '%m/%d/%Y')
    date_time_as_iso_string = str(date)
    date_as_iso_string = date_time_as_iso_string.split(' ')[0]
    return date_as_iso_string


organization_header_map = {
    'ResourceAgencyNum': 'id',
    'PublicName': 'name',
    'AgencyDescription': 'description',
    'AlternateName': 'alternate_name',
    'EmailAddressMain': 'email',
    'WebsiteAddress': 'url',
    'LastVerifiedOn': 'last_verified_on-x',
}


def parse_address_fields(header, value, addresses):
    output_address_header = address_header_map.get(get_normalized_address_header(header), None)
    is_physical_address_type = header.startswith('Physical')
    if output_address_header:
        index = 1 if is_physical_address_type else 0
        addresses[index][output_address_header] = value
        addresses[index]['type'] = 'physical_address' if is_physical_address_type else 'postal_address'


def get_normalized_address_header(fff):
    return re.sub(r'^Physical', 'Mailing', fff)


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


def parse_locations_fields(header, value, location):
    output_location_header = location_header_map.get(header, None)
    if output_location_header:
        if output_location_header in ['latitude', 'longitude']:
            try:
                value = float(value)
            except:
                value = None
        location[output_location_header] = value


location_header_map = {
    'ResourceAgencyNum': 'organization_id',
    'PublicName': 'name',
    'AlternateName': 'alternate_name',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
}


def parse_phone_number_fields(header, value, phone_numbers):
    output_phone_header = phone_header_map.get(phone_header_with_index_one(header), None)
    if output_phone_header:
        phone_index = get_zero_based_phone_index(header)
        set_phone_array_length(phone_numbers, phone_index)
        phone_numbers[phone_index][output_phone_header] = value
        if header == 'PhoneFax':
            phone_numbers[phone_index]['type'] = 'Fax'


def set_phone_array_length(phone_numbers, index):
    while index and len(phone_numbers) <= index:
        phone_numbers.append({})


def phone_header_with_index_one(phone_field_with_any_index):
    return re.sub(r'^Phone\d', 'Phone1', phone_field_with_any_index)


def get_zero_based_phone_index(phone):
    if phone == 'PhoneFax':
        return 5
    r = re.match(r'^Phone(\d)', phone)
    return int(r[1]) - 1 if r else None


phone_header_map = {
    'Phone1Number': 'number',
    'Phone1Type': 'type',
    'Phone1Name': 'description',  # there is also a field Phone1Description but BC211 does not appear to use it
    'PhoneFax': 'number',
}


def parse_taxonomy_fields(header, value, taxonomy_terms, vocabulary):
    if header in ['TaxonomyTerm', 'TaxonomyTerms', 'TaxonomyTermsNotDeactivated', 'TaxonomyCodes']:
        vocabulary = compute_vocabulary_name(vocabulary, header, value)
        taxonomy_terms += parse_taxonomy_terms(value, vocabulary)


def compute_vocabulary_name(vocabulary, header, value):
    if vocabulary:
        return vocabulary
    if header == 'TaxonomyCodes':
        return 'AIRS'
    if is_bc211_why(value):
        return 'bc211-why'
    if is_bc211_who(value):
        return 'bc211-who'
    return 'bc211-what'


def is_bc211_why(value):
    return value.islower()


def is_bc211_who(value):
    head = value[0]
    tail = value[1:-1]
    return head.isupper() and tail.islower()


def parse_taxonomy_terms(value, vocabulary):
    if vocabulary == 'AIRS':
        names = re.split(r'[;\* ]', value)
        names = [name.strip() for name in names]
    else:
        names = re.split(r'[;\-\*]', value)
        names = [name.strip() for name in names]
        names = [name.replace(' ', '-') for name in names]
        names = [name.replace('/', '-') for name in names]
    return [build_taxonomy_object(i, vocabulary) for i in names if i]


def build_taxonomy_object(name, vocabulary):
    return {'id': compute_hash(name, vocabulary),
            'name': name,
            'vocabulary': vocabulary,
            'parent_name': '',
            'parent_id': ''}


def compute_hash(*args):
    hasher = hashlib.sha1()
    for arg in args:
        hasher.update(arg.encode('utf-8'))
    return hasher.hexdigest()


def set_location_ids(location, addresses, phone_numbers, organization_or_service_id, parent_id):
    location['id'] = compute_location_id(location, addresses, phone_numbers)
    location['organization_id'] = pick_location_organization_id(organization_or_service_id, parent_id)


def compile_taxonomy_terms(taxonomy_terms, service_id, service_taxonomy_terms):
    for item in taxonomy_terms:
        the_id = compute_hash(service_id, item['id'])
        service_taxonomy_terms.append({'id': the_id,
                                       'service_id': service_id,
                                       'taxonomy_id': item['id'],
                                       'taxonomy_detail': '',
                                       })


def pick_location_organization_id(organization_or_service_id, parent_id):
    return organization_or_service_id if parent_id == '0' else parent_id


def write_location_to_sink(location, unique_location_ids, sink):
    if location['id'] not in unique_location_ids:
        sink.write_location(location)
        unique_location_ids[location['id']] = 1


def compute_location_id(location, addresses, phone_numbers):
    return compute_hash(compute_address_id(get_array_element_if_it_exists(addresses, 0)),
                        compute_address_id(get_array_element_if_it_exists(addresses, 1)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 0)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 1)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 2)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 3)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 4)),
                        compute_phone_number_id(get_array_element_if_it_exists(phone_numbers, 5)),
                        str(location.get('latitude', '')),
                        str(location.get('longitude', ''))
                        )


def get_array_element_if_it_exists(array, index):
    return array[index] if index < len(array) else None


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
    return phone_number.get('number', '') if phone_number else ''


def write_to_sink(addresses, location_id, phone_numbers, unique_phone_ids, taxonomy_terms,
                  unique_taxonomy_term_ids, service_taxonomy_terms, sink):
    write_addresses_to_sink(addresses, location_id, sink)
    write_phone_numbers_to_sink(phone_numbers, location_id, unique_phone_ids, sink)
    write_taxonomy_terms_to_sink(taxonomy_terms, unique_taxonomy_term_ids, sink)
    sink.write_service_taxonomy_terms(service_taxonomy_terms)


def write_addresses_to_sink(addresses, location_id, sink):
    for i, address in enumerate(addresses):
        if not address:
            continue
        address['id'] = str(uuid.uuid4())
        address['location_id'] = location_id
        sink.write_address(address)


def write_phone_numbers_to_sink(phone_numbers, location_id, phone_ids, sink):
    for i, phone_number in enumerate(phone_numbers):
        if 'number' not in phone_number or not phone_number['number']:
            continue
        the_id = compute_hash(phone_number['number'])
        if the_id in phone_ids:
            continue
        phone_number['id'] = the_id
        phone_number['location_id'] = location_id
        sink.write_phone_number(phone_number)
        phone_ids[the_id] = 1


def write_taxonomy_terms_to_sink(taxonomy_terms, unique_taxonomy_term_ids, sink):
    for term in taxonomy_terms:
        if term['id'] not in unique_taxonomy_term_ids:
            sink.write_taxonomy_term(term)
            unique_taxonomy_term_ids[term['id']] = 1
