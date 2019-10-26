from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from datahubhel.base_models import TimestampedUUIDModel
from datahubhel.core.models import Sensor


class Location(models.Model):
    name = models.CharField(verbose_name=_("address"), max_length=100)
    description = models.TextField(blank=True)
    location = models.PointField(
        verbose_name=_("location"),
        null=True,
        blank=True)

    def __str__(self):
        return self.name


class Thing(TimestampedUUIDModel):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ThingLocation(TimestampedUUIDModel):
    location = models.ForeignKey(
        Location,
        related_name='thinglocations',
        on_delete=models.PROTECT)
    thing = models.ForeignKey(
        Thing,
        related_name='thinglocations',
        on_delete=models.PROTECT)

    def __str__(self):
        return "{}--{}".format(self.location.name, self.thing.name)


class TA120Sensor(Sensor):
    key = models.CharField(max_length=128)
