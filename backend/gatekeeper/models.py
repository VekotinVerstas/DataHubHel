from django.conf import settings
from django.db import models

from datahubhel.base_models import EntityBase


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
