from django.db import models
from django.core import validators
from parler.models import TranslatableModel, TranslatedFields
from common.models import ValidateOnSaveMixin, RequiredCharField, OptionalCharField

class Organization(ValidateOnSaveMixin, TranslatableModel):
    id = RequiredCharField(primary_key=True, max_length=200, validators=[validators.validate_slug])
    website = OptionalCharField(max_length=200, validators=[validators.URLValidator()])
    email = OptionalCharField(max_length=200, validators=[validators.EmailValidator()])
    translations = TranslatedFields(
        name=models.CharField(blank=False, max_length=200),
        description=models.TextField(blank=True, null=True)
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
