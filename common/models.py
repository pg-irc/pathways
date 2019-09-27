from django.db import models
from django.core.exceptions import ValidationError


class ValidateOnSaveMixin(object):
    """Database model mixin which calls full_clean() from save(), to help
    ensure that no invalid data gets into the database. full_clean() replaces
    all empty values (including '') with None, which are saved as NULL, so there
    should be no empty strings in the database."""

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except ValidationError as error:
            raise self.build_validation_error_no_throw(error)
        return super(ValidateOnSaveMixin, self).save(*args, **kwargs)

    def build_validation_error_no_throw(self, error):
        try:
            type_of_self = type(self).__name__
            id_of_self = self.id
            message = error.__str__()
            return ValidationError('type={} id={} message={}'.format(type_of_self,
                                                                     id_of_self,
                                                                     message))
        except:
            return error

    def clean(self):
        self.set_empty_fields_to_null()
        super(ValidateOnSaveMixin, self).clean()

    def set_empty_fields_to_null(self):
        for field in self.all_fields():
            if self.is_empty(field):
                self.set_to_null(field)

    def all_fields(self):
        return self._meta.fields

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


class OptionalTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super(OptionalTextField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(OptionalTextField, self).deconstruct()
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


class RequiredURLField(models.URLField):
    def __init__(self, *args, **kwargs):
        kwargs['null'] = False
        kwargs['blank'] = False
        super(RequiredURLField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RequiredURLField, self).deconstruct()
        kwargs.pop('null', None)
        kwargs.pop('blank', None)
        return name, path, args, kwargs
