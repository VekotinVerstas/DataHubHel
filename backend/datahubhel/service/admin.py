from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Service, ServiceToken


class ServiceAdmin(admin.ModelAdmin):
    exclude = (
        'password',
        'last_login',
        'client',
    )


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceToken, ModelAdmin)
