from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class TokenBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if 'token' not in request.GET or username or password:
            return

        try:
            user = UserModel._default_manager.get(auth_token=request.GET.get('token'))
        except UserModel.DoesNotExist:
            return

        if self.user_can_authenticate(user):
            return user
