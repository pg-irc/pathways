from bc211.import_open_referral_csv.organization import import_organizations_file
from bc211.import_open_referral_csv.service import import_services_file
from bc211.import_open_referral_csv.location import import_locations_file
from bc211.import_open_referral_csv.service_at_location import import_services_at_location_file
from bc211.import_open_referral_csv.address import import_addresses_file
from bc211.import_open_referral_csv.phone import import_phones_file
from bc211.import_open_referral_csv.taxonomy import import_taxonomy_file
from bc211.import_open_referral_csv.service_taxonomy import import_services_taxonomy_file
from bc211.import_open_referral_csv.import_missing_coordinates import import_missing_coordinates

def import_open_referral_files(root_folder, collector, counters, city_latlong_map):
    import_organizations_file(root_folder, collector, counters)
    import_services_file(root_folder, collector, counters)
    import_locations_file(root_folder, collector, counters)
    import_services_at_location_file(root_folder, collector, counters)
    import_addresses_file(root_folder, collector, counters)
    import_phones_file(root_folder, collector, counters)
    import_taxonomy_file(root_folder, counters)
    import_services_taxonomy_file(root_folder, collector)
    if city_latlong_map:
        import_missing_coordinates(city_latlong_map)
