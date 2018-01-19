from common.models import ValidateOnSaveMixin, RequiredCharField
from django.core import validators
from django.db import models
from django.db.models import Q
from organizations.models import Organization
from parler.models import TranslatableModel, TranslatedFields
from taxonomies.models import TaxonomyTerm
from services import details

class Service(ValidateOnSaveMixin, TranslatableModel):
    id = RequiredCharField(primary_key=True,
                           max_length=200,
                           validators=[validators.validate_slug])

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     related_name='services')

    taxonomy_terms = models.ManyToManyField(TaxonomyTerm,
                                            db_table='services_service_taxonomy_terms')

    translations = TranslatedFields(name=models.CharField(max_length=200),
                                    description=models.TextField(blank=True, null=True))

    def __str__(self):
        return self.name

    @classmethod
    def get_queryset(cls, search_parameters):
        queryset = cls.objects.all()
        queryset = cls.add_taxonomy_filter_if_given(queryset, search_parameters)
        queryset = cls.add_full_text_search_filter_if_given(queryset, search_parameters)
        queryset = cls.add_sorting_and_paging_if_given(queryset, search_parameters)
        return queryset

    @staticmethod
    def add_taxonomy_filter_if_given(queryset, search_parameters):
        identifier = search_parameters.taxonomy_id
        term = search_parameters.taxonomy_term

        if identifier and term:
            queryset = queryset.filter(taxonomy_terms__taxonomy_id=identifier,
                                       taxonomy_terms__name=term)
        return queryset

    @staticmethod
    def add_full_text_search_filter_if_given(queryset, search_parameters):
        search_terms = search_parameters.full_text_search_terms
        if not search_terms:
            return queryset

        builder = details.FilterBuilder()
        for term in search_terms:
            builder.add_with_or(Q(translations__name__icontains=term),
                                Q(translations__description__icontains=term))

        return queryset.filter(builder.get_filter())

    @staticmethod
    def add_sorting_and_paging_if_given(queryset, search_parameters):
        if not search_parameters.sort_by:
            return queryset
        return queryset.order_by(search_parameters.sort_by)
