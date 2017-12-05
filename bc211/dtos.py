from bc211 import validators

class Organization:
    def __init__(self, id, name, description, website, email, locations):
        self.id = id
        self.name = name
        self.description = description
        self.website = website
        self.email = email
        self.locations = locations

class Location:
    def __init__(self, id, name, organization_id, description, spatial_location):
        self.id = id
        self.name = name
        self.organization_id = organization_id
        self.description = description
        self.spatial_location = spatial_location

class SpatialLocation:
    def __init__(self, latitude, longitude):
        self.latitude = validators.validate_float(latitude)
        self.longitude = validators.validate_float(longitude)
