from django.conf import settings
from django.db import models


class EntityBase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    sts_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Thing(EntityBase):
    class Meta:
        verbose_name = 'thing'
        verbose_name_plural = 'things'


class Datastream(EntityBase):
    thing = models.ForeignKey(Thing)

    class Meta:
        verbose_name = 'data stream'
        verbose_name_plural = 'data streams'
