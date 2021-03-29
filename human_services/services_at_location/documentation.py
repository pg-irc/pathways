from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from human_services.services_at_location.serializers import ServiceAtLocationSerializer
from common import documentation
from common.filter_parameter_parsers import ProximityParser, TaxonomyParser


def get_service_at_location_list_schema():
    operation_description = 'Get a list of services at locations'
    manual_parameters = ([documentation.get_proximity_sort_manual_parameter(),
                          documentation.get_proximity_filter_manual_parameter(),
                          documentation.get_proximity_filter_radius_manual_parameter(),
                          documentation.get_taxonomy_terms_manual_parameter(),
                          documentation.get_page_manual_parameter(),
                          documentation.get_related_to_topic_manual_parameter(),
                          documentation.get_region_filter_manual_parameter()])
    responses = {
        200: openapi.Response('A list of zero or more services at locations',
                              ServiceAtLocationSerializer(many=True)),
        400: (', '.join(ProximityParser.errors_to_list() + TaxonomyParser.errors_to_list())),
        404: 'Invalid page',
    }

    return swagger_auto_schema(operation_description=operation_description,
                               manual_parameters=manual_parameters,
                               responses=responses,
                               )
