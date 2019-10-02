from django.contrib.gis.db import models
from common.models import (RequiredURLField,
                           OptionalTextField, RequiredCharField)


class Algorithm(models.Model):
    url = RequiredURLField()
    name = RequiredCharField(max_length=200)
    notes = OptionalTextField()


class SearchLocation(models.Model):
    name = OptionalTextField()
    point = models.PointField(blank=True, null=True)
