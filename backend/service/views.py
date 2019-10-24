from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from datahubhel.dhh_auth.models import ClientPermission
from service.permissions import ServicePermissions

from .models import Service, ServiceToken
from .serializers import SerializerPermissionSerializer, ServiceKeySerializer, ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [
        ServicePermissions,
    ]


class ServiceTokenViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceKeySerializer

    def get_queryset(self):
        user = self.request.user
        keys = ServiceToken.objects.filter(
            service__maintainers__in=[user]
        )
        return keys


class ServicePermissionsViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    queryset = ClientPermission.objects.filter(client__service__in=Service.objects.all())
    serializer_class = SerializerPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        client = user.client

        q_filters = Q(client=client)
        if isinstance(user, get_user_model()):
            q_filters |= Q(permitted_by=user)

        return ClientPermission.objects.filter(q_filters)
