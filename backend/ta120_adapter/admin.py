from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Location, TA120Sensor, Thing, ThingLocation


admin.site.register(TA120Sensor, ModelAdmin)
admin.site.register(Thing, ModelAdmin)
admin.site.register(ThingLocation, ModelAdmin)


@admin.register(Location)
class ThingAdmin(OSMGeoAdmin):
    ordering = ('name',)
