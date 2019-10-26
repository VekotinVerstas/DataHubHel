from django.db import models

from datahubhel.base_models import EntityBase, TimestampedUUIDModel


class Thing(EntityBase):
    class Meta:
        verbose_name = 'thing'
        verbose_name_plural = 'things'
        permissions = (
            ('view_thing_location', 'Can view thing location'),
            ('view_thing_location_history', 'Can view thing location history')
        )


class Datastream(EntityBase):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'data stream'
        verbose_name_plural = 'data streams'
        permissions = (
            ('view_datastream', 'Can view datastream'),
            ('create_observation', 'Can create observation to datastream'),
        )


class Sensor(TimestampedUUIDModel):
    sensor_id = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60)
    sensor_type = models.CharField(max_length=60)
    thing = models.ForeignKey(Thing, on_delete=models.PROTECT)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
