from bc211 import exceptions
from django.utils.text import slugify

def required_string(field, values):
    value = values.get(field)
    if isinstance(value, str):
        return value
    raise exceptions.MissingRequiredFieldXmlParseException(field)

def required_slug(field, values):
    value = values.get(field)
    if isinstance(value, str):
        return slugify(value)
    raise exceptions.MissingRequiredFieldXmlParseException(field)

def optional_string(field, values):
    value = values.get(field)
    if value is None or isinstance(value, str):
        return value
    raise exceptions.InvalidNestedObjectXmlParseException(field)

def optional_object(the_class, field, values):
    value = values.get(field)
    if value is None or isinstance(value, the_class):
        return value
    raise exceptions.InvalidNestedObjectXmlParseException(field)

def optional_list_of_objects(the_class, field, values):
    value = values.get(field)
    if isinstance(value, list):
        if not value:
            return value
        for item in value:
            if not isinstance(item, the_class):
                raise exceptions.InvalidTypeXmlParseException(item)
        return value
    raise exceptions.InvalidTypeXmlParseException(value)

def required_float(field, values):
    value = values.get(field)
    return parse_float(value)

def parse_float(value):
    try:
        return float(value)
    except ValueError:
        raise exceptions.InvalidFloatXmlParseException(value)

def required_int(field, values):
    value = values.get(field)
    if isinstance(value, int):
        return value
    raise exceptions.MissingRequiredFieldXmlParseException(field)
