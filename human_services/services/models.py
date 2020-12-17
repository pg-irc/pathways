from common.models import ValidateOnSaveMixin, RequiredCharField, OptionalCharField
from django.core import validators
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from human_services.organizations.models import Organization
from taxonomies.models import TaxonomyTerm


class Service(ValidateOnSaveMixin, TranslatableModel):
    id = RequiredCharField(primary_key=True,
                           max_length=200,
                           validators=[validators.validate_slug])
    organization = models.ForeignKey(Organization,
                                     on_delete=models.PROTECT,
                                     related_name='services')
    taxonomy_terms = models.ManyToManyField(TaxonomyTerm,
                                            db_table='services_service_taxonomy_terms')
    translations = TranslatedFields(name=models.CharField(max_length=255),
                                    alternate_name=models.CharField(blank=True, max_length=255),
                                    description=models.TextField(blank=True, null=True))
    email = OptionalCharField(max_length=200, validators=[validators.EmailValidator()])
    website = OptionalCharField(max_length=255, validators=[validators.URLValidator()])
    last_verified_date = models.DateField(blank=True, null=True)
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
