from django.conf import settings
from django.db import models


class EntityBase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    sts_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


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
