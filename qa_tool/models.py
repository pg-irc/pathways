from django.db import models
from common.models import (RequiredURLField,
                           OptionalTextField, RequiredCharField)


class Algorithm(models.Model):
    url = RequiredURLField()
    name = RequiredCharField(max_length=200)
    notes = OptionalTextField()
