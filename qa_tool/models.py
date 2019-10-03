from django.contrib.gis.db import models
from common.models import (RequiredURLField,
                           OptionalTextField, RequiredCharField)
from human_services.services.models import Service
from users.models import User


class Algorithm(models.Model):
    url = RequiredURLField()
    name = RequiredCharField(max_length=200)
    notes = OptionalTextField()


class SearchLocation(models.Model):
    name = OptionalTextField()
    point = models.PointField(blank=True, null=True)


class Score(models.Model):
    value = models.IntegerField()
    time_stamp = models.DateTimeField()
    algorithm = models.ForeignKey(Algorithm, on_delete=models.PROTECT)
    search_location = models.ForeignKey(SearchLocation, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
