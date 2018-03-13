from rest_framework import generics, permissions, serializers

from ..models import User
from ._utils import get_user_id_from_request

VISIBLE_USER_FIELDS = [
    'id',
    'first_name',
    'last_name',
    'email',
    'date_joined',
]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = VISIBLE_USER_FIELDS
        read_only_fields = ['id', 'date_joined']


class UserCreationSerializer(UserSerializer):
    class Meta:
        model = User
        fields = VISIBLE_USER_FIELDS
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'id': {'read_only': False},
            'username': {'write_only': True},
        }

    def validate(self, attrs):
        user_id = attrs['id']
        if User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError(
                "Already registered", code='already-registered')
        attrs['username'] = 'u{}'.format(user_id).replace('-', '')
        return super().validate(attrs)


class MePermission(permissions.BasePermission):
    """
    Permission to "me" endpoint, i.e. user's own profile.
    """

    def has_permission(self, request, view):
        return bool(get_user_id_from_request(request))

    def has_object_permission(self, request, view, obj):
        return get_user_id_from_request(request) == obj.id


class UserView(generics.GenericAPIView):
    permission_classes = [MePermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        queryset = self.get_queryset()
        user = generics.get_object_or_404(queryset)
        self.check_object_permissions(self.request, user)
        return user

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = get_user_id_from_request(self.request)
        return queryset.filter(id__in=[user_id])


class MeView(UserView, generics.RetrieveAPIView, generics.UpdateAPIView):
    """
    The "me" endpoint to retrieve or update user's own profile.
    """
    pass


class RegisterView(UserView, generics.CreateAPIView):
    serializer_class = UserCreationSerializer

    autofilled_fields = ['first_name', 'last_name', 'email']

    def create(self, request, *args, **kwargs):
        request.data['id'] = get_user_id_from_request(request)
        user = getattr(request, 'user', None)
        for field in self.autofilled_fields:
            request.data.setdefault(field, getattr(user, field, None))
        return super().create(request, *args, **kwargs)


class ForgetView(UserView, generics.DestroyAPIView):
    pass
