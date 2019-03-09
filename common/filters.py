from rest_framework import filters
from config.settings.base import SRID
from django.contrib.gis.geos import Point
from django.db.models import F
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance as DistanceMeasure
from common.filter_parameter_parsers import ProximityParser, TaxonomyParser
from human_services.locations.models import ServiceAtLocation
from human_services.services.models import Service
import logging

LOGGER = logging.getLogger(__name__)


class MultiFieldOrderingFilter(filters.OrderingFilter):
    REVERSE_SORT_PREFIX = '-'
    ordering_description = ('Fields for sorting of results. Enter one or more fields separated '
                            'by space or comma. Records that sort equally by the first field are '
                            'sorted by the second field, etc. Prefix any field with '
                            + REVERSE_SORT_PREFIX + ' for sorting in descending order.')

    def get_ordering(self, request, queryset, view):
        argument_string = request.query_params.get(self.ordering_param)
        if argument_string:
            arguments = argument_string.replace(',', ' ').split()
            return (self.set_prefix(argument) for argument in arguments if argument)
        return None

    def set_prefix(self, argument):
        argument = argument.strip()
        reverse_sort = argument[0:1] == self.REVERSE_SORT_PREFIX
        stripped_argument = argument[1:] if reverse_sort else argument

        translated_fields = ['name', 'description']
        if stripped_argument not in translated_fields:
            return argument

        argument = 'translations__' + stripped_argument
        return self.REVERSE_SORT_PREFIX + argument if reverse_sort else argument


class SearchFilter(filters.SearchFilter):
    search_description = ('Search terms for full text search. Enter one or more terms separated '
                          'by space or comma. Logical AND is implied among the terms. TODO '
                          'currently only looks in name and description, make it look more '
                          'widely.')


class ProximityFilter(filters.BaseFilterBackend):
    filter_description = ('Order by proximity to a point. '
                          'Accepts two comma separated values representing a longitude and a latitude. '
                          'Example: "-123.1207,+49.2827".')

    def filter_queryset(self, request, queryset, view):
        proximity_parameter = request.query_params.get('proximity', None)
        if proximity_parameter:
            proximity = ProximityParser(proximity_parameter)
            if queryset.model is ServiceAtLocation:
                reference_point = Point(proximity.latitude, proximity.longitude, srid=SRID)
                queryset = (queryset
                            .annotate(distance=Distance('location__point', reference_point))
                            .order_by('distance'))
        return queryset


class ProximityCutoffFilter(filters.BaseFilterBackend):
    filter_description = ('Exclude results more than 25KM (hard-coded value) from a given point. '
                          'Accepts two comma separated values representing a longitude and a latitude. '
                          'Example: "-123.1207,+49.2827".')

    def filter_queryset(self, request, queryset, view):
        user_location = request.query_params.get('user_location', None)
        if user_location and queryset.model is ServiceAtLocation:
            location = ProximityParser(user_location)
            location_point = Point(location.latitude, location.longitude, srid=SRID)
            queryset = (queryset
                        .annotate(distance=Distance('location__point', location_point))
                        .filter(distance__lte=DistanceMeasure(km=25)))
        return queryset


class ServiceSimilarityFilter(filters.BaseFilterBackend):
    filter_description = (
        'Order by relatedness to the task with the given task id. '
        'Services with missing similarity score in the database are omitted from the result'
    )

    def filter_queryset(self, request, queryset, view):
        if queryset.model is not ServiceAtLocation:
            return queryset

        task_id = request.query_params.get('related_to_task', None)
        if not task_id:
            return queryset

        LOGGER.warning('Task id "%s"', task_id)

        return (queryset.
                annotate(score=F('service__taskservicesimilarityscore__similarity_score')).
                annotate(task_id=F('service__taskservicesimilarityscore__task_id')).
                filter(task_id__exact=task_id).
                order_by('-score'))


class TaxonomyFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        taxonomy_parameter = request.query_params.get('taxonomy_terms', None)
        if taxonomy_parameter:
            taxonomy_terms = TaxonomyParser(taxonomy_parameter).terms
            for term in taxonomy_terms:
                if queryset.model is Service:
                    queryset = queryset.filter(taxonomy_terms__taxonomy_id=term[0],
                                               taxonomy_terms__name=term[1])
                elif queryset.model is ServiceAtLocation:
                    queryset = queryset.filter(service__taxonomy_terms__taxonomy_id=term[0],
                                               service__taxonomy_terms__name=term[1])
        return queryset


class LocationIdFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        location_id = view.kwargs.get('location_id', None)
        if location_id:
            if queryset.model is Service:
                queryset = queryset.filter(locations__id=location_id)
            elif queryset.model is ServiceAtLocation:
                queryset = queryset.filter(location_id=location_id)
        return queryset


class ServiceIdFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        service_id = view.kwargs.get('service_id', None)
        if service_id:
            if queryset.model is ServiceAtLocation:
                queryset = queryset.filter(service_id=service_id)
        return queryset


class OrganizationIdFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        organization_id = view.kwargs.get('organization_id', None)
        if organization_id:
            if queryset.model is Service:
                queryset = queryset.filter(organization_id=organization_id)
        return queryset
