from django.db import models
from django.core import validators
from parler.models import TranslatableModel

def contains_no_spaces():
    return validators.RegexValidator(regex=r'^[^ ]+$')


class ValidateOnSaveMixin(object):
    """Database model class which calls full_clean() from save(), to help
    ensure that no invalid data gets into the database. full_clean() replaces
    all empty values (including '') with None, which are saves as NULL,so there
    should be no empty strings in the database."""

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ValidateOnSaveMixin, self).save(*args, **kwargs)

    def clean(self):
        self.set_empty_fields_to_null()
        super(ValidateOnSaveMixin, self).clean()

    def set_empty_fields_to_null(self):
        for field in self.all_fields():
            if self.can_be_null(field) and self.is_empty(field):
                self.set_to_null(field)

    def all_fields(self):
        return self._meta.fields

    def can_be_null(self, field):
        return field.null

    def is_empty(self, field):
        value = getattr(self, field.attname)
        return value in field.empty_values

    def set_to_null(self, field):
        setattr(self, field.attname, None)


class OptionalCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super(OptionalCharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(OptionalCharField, self).deconstruct()
        kwargs.pop('null', None)
        kwargs.pop('blank', None)
        return name, path, args, kwargs


class RequiredCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = False
        kwargs['blank'] = False
        super(RequiredCharField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RequiredCharField, self).deconstruct()
        kwargs.pop('null', None)
        kwargs.pop('blank', None)
        return name, path, args, kwargs
