from bc211 import validate

class Organization:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.description = validate.optional_string('description', kwargs)
        self.website = validate.optional_string('website', kwargs)
        self.email = validate.optional_string('email', kwargs)
        self.locations = kwargs.get('locations', [])


class Location:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.organization_id = validate.required_string('organization_id', kwargs)
        self.description = validate.optional_string('description', kwargs)
        self.spatial_location = validate.optional_object(SpatialLocation, 'spatial_location', kwargs)
        self.services = validate.optional_list_of_objects(Service, 'services', kwargs)
        self.physical_address = validate.optional_object(Address, 'physical_address', kwargs)
        self.postal_address = validate.optional_object(Address, 'postal_address', kwargs)
        self.phone_numbers = validate.optional_list_of_objects(PhoneAtLocation, 'phone_numbers', kwargs)


class SpatialLocation:
    def __init__(self, **kwargs):
        self.latitude = validate.required_float('latitude', kwargs)
        self.longitude = validate.required_float('longitude', kwargs)


class Service:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.organization_id = validate.required_string('organization_id', kwargs)
        self.site_id = validate.required_string('site_id', kwargs)
        self.description = validate.optional_string('description', kwargs)
        self.taxonomy_terms = kwargs.get('taxonomy_terms', [])
        self.last_verified_date = kwargs.get('last_verified_date', kwargs)


class TaxonomyTerm:
    def __init__(self, **kwargs):
        self.taxonomy_id = validate.required_slug('taxonomy_id', kwargs)
        self.name = validate.required_slug('name', kwargs)


class Address:
    def __init__(self, **kwargs):
        self.address_lines = validate.optional_string('address_lines', kwargs)
        self.city = validate.required_string('city', kwargs)
        self.state_province = validate.optional_string('state_province', kwargs)
        self.postal_code = validate.optional_string('postal_code', kwargs)
        self.country = validate.required_string('country', kwargs)
        self.location_id = validate.required_string('location_id', kwargs)
        self.address_type_id = validate.required_string('address_type_id', kwargs)

class PhoneAtLocation:
    def __init__(self, **kwargs):
        self.location_id = validate.required_string('location_id', kwargs)
        self.phone_number_type_id = validate.required_string('phone_number_type_id', kwargs)
        self.phone_number = validate.required_string('phone_number', kwargs)
