from rest_framework import permissions, serializers, viewsets
from rest_framework.authtoken.models import Token

from ._utils import get_user_id_from_request


class TokenSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-token-detail')

    class Meta:
        model = Token
        fields = ['url', 'key', 'created', 'user_id']
        read_only_fields = ['url', 'key', 'created', 'user_id']


class OwnTokensPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(get_user_id_from_request(request))

    def has_object_permission(self, request, view, obj):
        return get_user_id_from_request(request) == obj.user.id


class TokenViewSet(viewsets.ModelViewSet):
    permission_classes = [OwnTokensPermission]
    serializer_class = TokenSerializer
    queryset = Token.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = get_user_id_from_request(self.request)
        return queryset.filter(user__id=user_id)
