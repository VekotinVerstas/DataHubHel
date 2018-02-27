from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from gatekeeper.models import Datastream

from .models import Service, ServiceToken


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    keys = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='servicetoken-detail',
    )

    class Meta:
        model = Service
        fields = (
            'id',
            'url',
            # 'maintainers',
            'name',
            'description',
            'keys',
        )


class ServiceKeySerializer(serializers.HyperlinkedModelSerializer):
    key = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = ServiceToken
        fields = (
            'id',
            'url',
            'service',
            'key',
        )


class SerializerPermissionSerializer(serializers.Serializer):
    # TODO Accept STS entity ids instead of internal ids
    PERMISSION_CHOICES = [
        ('view_datastream', 'View datastream'),
    ]
    ENTITY_CHOICES = [
        ('datastream', 'Datastream'),
    ]
    ENTITY_MODEL_MAP = {
        'datastream': Datastream,
    }

    service = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='service-detail',
        queryset=Service.objects.all(),
    )

    permission = serializers.ChoiceField(
        choices=PERMISSION_CHOICES,
    )
    entity_type = serializers.ChoiceField(
        choices=ENTITY_CHOICES
    )
    entity_id = serializers.CharField()

    url = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='servicepermission-detail',
        read_only=True,
    )

    id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
    )

    class Meta:
        fields = (
            'service',
            'permission',
            'entity_type',
            'entity_id',
            'url',
        )

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        service = validated_data['service']
        entity_model = self.ENTITY_MODEL_MAP[validated_data['entity_type']]

        entity = entity_model.objects.filter(
            sts_id=validated_data['entity_id'],
            owner=user
        ).first()

        if not entity:
            raise ValidationError({
                'entity_id': [_('No such entity')]
            })

        return service.client.create_perm(validated_data['permission'], entity, user)

    def to_representation(self, instance):
        fields = self.fields
        service = instance.client.service
        permission = instance.permission.codename
        entity_id = instance.object_pk

        model_name = str(instance.content_type.model)
        entity_type = model_name

        ret = OrderedDict()
        ret['url'] = fields['url'].to_representation(instance)
        ret['id'] = fields['id'].to_representation(instance)
        ret['service'] = fields['service'].to_representation(service)
        ret['permission'] = fields['permission'].to_representation(permission)
        ret['entity_id'] = fields['entity_id'].to_representation(entity_id)
        ret['entity_type'] = fields['entity_type'].to_representation(entity_type)

        return ret
