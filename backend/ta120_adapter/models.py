from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from utils.models import TimestampedUUIDModel


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


class Sensor(TimestampedUUIDModel):
    sensor_id = models.CharField(max_length=60, unique=True)
    key = models.CharField(max_length=128)

    name = models.CharField(max_length=60)
    sensor_type = models.CharField(max_length=60)
    thing = models.ForeignKey(Thing, on_delete=models.PROTECT)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
