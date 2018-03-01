from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import Client, ClientPermission, User

admin.site.register(User, UserAdmin)
admin.site.register(Client, ModelAdmin)
admin.site.register(ClientPermission, ModelAdmin)
