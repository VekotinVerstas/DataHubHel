from django.contrib import admin
from django.contrib.admin import ModelAdmin

from datahubhel.core.models import Datastream, Thing

admin.site.register(Datastream, ModelAdmin)
admin.site.register(Thing, ModelAdmin)
