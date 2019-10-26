from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from gatekeeper.models import Datastream


class Observation(models.Model):
    id = models.CharField(_("id"), max_length=70, primary_key=True)
    time = models.DateTimeField(_("time"))
    sensor_id = models.CharField(_("sensor_id"), max_length=50)
    property_name = models.CharField(_("property_name"), max_length=50)
    property_value = JSONField()
    datastream = models.ForeignKey(Datastream, on_delete=models.PROTECT, related_name='observations')

    def __str__(self):
        return f'{self.property_name}-{self.sensor_id}'
