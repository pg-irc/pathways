from rest_framework import filters, serializers
from config.settings.base import SRID
from django.contrib.gis.geos import Point
from django.db.models import F
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance as DistanceMeasure
from content.models import Alert
from common.filter_parameter_parsers import ProximityParser, TaxonomyParser
from human_services.locations.models import ServiceAtLocation
from human_services.services.models import Service


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


class TopicSimilarityAndProximitySortFilter(filters.BaseFilterBackend):
    filter_description = (
        'Given both a topic and a user location, rank returned services by '
        'similarity to the topic and the distance to the user'
    )

    def filter_queryset(self, request, queryset, view):
        if queryset.model is not ServiceAtLocation:
            return queryset

        proximity_parameter = request.query_params.get('proximity', None)
        topic_id = request.query_params.get('related_to_topic', None)

        if proximity_parameter and topic_id:
            return self.sort_by_proximity_and_topic(queryset, proximity_parameter, topic_id)

        if topic_id:
            return self.sort_by_topic_similarity(queryset, topic_id)

        if proximity_parameter:
            return self.sort_by_proximity(queryset, proximity_parameter)

        return queryset

    def sort_by_proximity_and_topic(self, queryset, proximity_parameter, topic_id):
        reference_point = self.to_point(proximity_parameter)
        return (queryset.
                annotate(distance=Distance('location__point', reference_point)).
                annotate(inverse_score=F('distance')/F('service__taskservicesimilarityscore__similarity_score')).
                annotate(task_id=F('service__taskservicesimilarityscore__task_id')).
                filter(task_id__exact=topic_id).
                order_by('inverse_score'))

    def to_point(self, proximity_parameter):
        proximity = ProximityParser(proximity_parameter)
        return Point(proximity.latitude, proximity.longitude, srid=SRID)

    def sort_by_topic_similarity(self, queryset, topic_id):
        return (queryset.
                annotate(score=F('service__taskservicesimilarityscore__similarity_score')).
                annotate(task_id=F('service__taskservicesimilarityscore__task_id')).
                filter(task_id__exact=topic_id).
                order_by('-score'))

    def sort_by_proximity(self, queryset, proximity_parameter):
        reference_point = self.to_point(proximity_parameter)
        return (queryset
                .annotate(distance=Distance('location__point', reference_point))
                .order_by('distance'))


class ProximityCutoffFilter(filters.BaseFilterBackend):
    filter_description = ('Exclude results more than a given distance in KM from a given point. '
                          'Accepts two comma separated values representing a longitude and a latitude. '
                          'Example: "-123.1207,+49.2827". Use radius_km to specify the distance to use')

    def filter_queryset(self, request, queryset, view):
        user_location = request.query_params.get('user_location', None)
        if user_location and queryset.model is ServiceAtLocation:
            radius_km = self.get_valid_radius_km(request)
            location = ProximityParser(user_location)
            location_point = Point(location.latitude, location.longitude, srid=SRID)
            queryset = (queryset
                        .annotate(distance=Distance('location__point', location_point))
                        .filter(distance__lte=DistanceMeasure(km=radius_km)))
        return queryset

    def get_valid_radius_km(self, request):
        default_radius_km = '25'
        return self.validate_radius(request.query_params.get('radius_km', default_radius_km))

    def validate_radius(self, radius):
        radius_as_number = self.to_number_or_none(radius)
        if not radius_as_number or radius_as_number < 0:
            self.throw_error()
        return radius_as_number

    def to_number_or_none(self, radius):
        try:
            return float(radius)
        except ValueError:
            return None

    def throw_error(self):
        message = 'Invalid value for radius_km, must be a positive number'
        raise serializers.ValidationError(message)


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

class AlertIdFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        alert_id = view.kwargs.get('alert_id', None)
        if alert_id:
            if queryset.model is Alert:
                queryset = queryset.filter(alert_id=alert_id)
        return queryset

class RegionFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        region = request.query_params.get('region', None)
        if region:
            if queryset.model is ServiceAtLocation:
                service_id_suffix = '_{0}'.format(region.lower())
                queryset = queryset.filter(service_id__id__endswith=service_id_suffix)
        return queryset
