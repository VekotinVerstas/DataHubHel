from rest_framework import serializers

from .models import ClientPermission


class ClientPermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClientPermission
        fields = (
            'id',
            'url',
            'client',
            'entity_type',
            'entity_id',
        )
