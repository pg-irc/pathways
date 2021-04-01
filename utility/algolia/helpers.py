import csv
import json


def parse_cities_csv(csv_path):
    with open(csv_path, mode='r') as file:
        csv_reader = csv.reader(file)
        city_to_latlong = {rows[0]: {'lng': float(rows[1]), 'lat': float(rows[2])} for rows in csv_reader}
        return city_to_latlong


def read_phone_data(phone_data_path):
    result = {}
    with open(phone_data_path) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            location_id = row[0]
            phone_number = row[1]
            phone_number_type_id = row[2]

            if location_id not in result:
                result[location_id] = []
            result[location_id].append({'phone_number': phone_number, 'type': phone_number_type_id})

    return result


def read_taxonomy_data(taxonomy_data_path):
    result = {}
    with open(taxonomy_data_path) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            service_id = row[0]
            taxonomy_term = row[1]

            if service_id not in result:
                result[service_id] = []
            result[service_id].append(taxonomy_term)
    return result


def read_algolia_data(algolia_data_path):
    with open(algolia_data_path, 'r') as file:
        return json.loads(file.read())


def set_phone_numbers_on_services(algolia_data, phone_data):
    for service in algolia_data:
        location_id = service['location_id']
        if location_id in phone_data:
            service['phone_numbers'] = phone_data[location_id]
        else:
            service['phone_numbers'] = []
    return algolia_data


def set_taxonomy_terms_on_services(algolia_data, taxonomy_data):
    for service in algolia_data:
        service_id = service['service_id']
        if service_id in taxonomy_data:
            service['taxonomy_terms'] = taxonomy_data[service_id]
            if 'immigrantsethnocultural-groups' in taxonomy_data[service_id]:
                service['for_newcomers'] = 1
            else:
                service['for_newcomers'] = 0
        else:
            service['taxonomy_terms'] = []
    return algolia_data
