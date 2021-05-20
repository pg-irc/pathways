from drf_yasg2 import openapi


def get_proximity_sort_manual_parameter():
    return (openapi.Parameter('proximity',
                              openapi.IN_QUERY,
                              description=('Order by proximity to a point. Accepts two comma separated values '
                                           'representing a longitude and a latitude. Example: "-123.1207,+49.2827".'),
                              type=openapi.TYPE_STRING,
                              # Regex representing a latitude and longitude.
                              # Valid patterns consist of two integers or floats, comma separated, with
                              # optional + or - prefixes. One space after the comma is allowed here.
                              pattern=r'^[-+]?[0-9]+\.?[0-9]*,\s?[-+]?[0-9]+\.?[0-9]*$'))


def get_proximity_filter_manual_parameter():
    return (openapi.Parameter('user_location',
                              openapi.IN_QUERY,
                              description=('Filter by proximity to a point. Accepts two comma separated values '
                                           'representing a longitude and a latitude. Example: "-123.1207,+49.2827".'),
                              type=openapi.TYPE_STRING,
                              # Regex representing a latitude and longitude.
                              # Valid patterns consist of two integers or floats, comma separated, with
                              # optional + or - prefixes. One space after the comma is allowed here.
                              pattern=r'^[-+]?[0-9]+\.?[0-9]*,\s?[-+]?[0-9]+\.?[0-9]*$'))


def get_proximity_filter_radius_manual_parameter():
    return (openapi.Parameter('radius_km',
                              openapi.IN_QUERY,
                              description=('Set the radius in KM used for filtering by proximity '
                                           'to a point. Accepts a positive number.'),
                              type=openapi.TYPE_NUMBER))


def get_related_to_topic_manual_parameter():
    return (openapi.Parameter('related_to_topic',
                              openapi.IN_QUERY,
                              description=('Order by services\' similarity to a given topic. Accepts a topic id.'),
                              type=openapi.TYPE_STRING,
                              pattern=r'^[a-zA-Z0-9\-\_]+$'))


def get_taxonomy_terms_manual_parameter():
    return (openapi.Parameter('taxonomy_terms',
                              openapi.IN_QUERY,
                              description=('Filter result on taxonomic terms, specify one or more terms of the '
                                           'form taxonomy.term, separated by comma. Examples: '
                                           '"bc211-what.libraries", "bc211-who.service-providers", '
                                           '"bc211-why.homelessness". If more than one term is given, records '
                                           'returned are those that are annotated with all specified terms. TODO '
                                           'make this work for hierarchical taxonomies.'),
                              type=openapi.TYPE_STRING,
                              # One term followed by comma and additional terms zero or more times,
                              # where a term consits of one or more letters/dashes, a dot, and more
                              # letters/dashes. White space is allowed around the comma but not the
                              # dots
                              pattern=r'^[\w\-]+\.[\w\-]+(\W*,\W*[\w\-]+\.[\w\-]+)*$'))


def get_page_manual_parameter():
    return (openapi.Parameter('page',
                              openapi.IN_QUERY,
                              description=('A page number within the paginated result set. When returning a paginated '
                                           'result, the response contains a Count header with the total number of '
                                           'entries in the result, and a Link header with links to first, prev, next '
                                           'and last pages in the result'),
                              type=openapi.TYPE_STRING,
                              # 1 to 2 digit number
                              pattern=r'^[1-9][0-9]*$'))


def get_region_filter_manual_parameter():
    return (openapi.Parameter('region',
                              openapi.IN_QUERY,
                              description=('Filter services at location by a given region. Accepts a string representing a region. '
                              'Example: "bc"'),
                              type=openapi.TYPE_STRING))