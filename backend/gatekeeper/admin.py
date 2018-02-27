from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Datastream, Thing

admin.site.register(Datastream, ModelAdmin)
admin.site.register(Thing, ModelAdmin)
