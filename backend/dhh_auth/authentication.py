from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token


class ClientTokenAuthentication(TokenAuthentication):
    """
    Token authentication for user models with client support
    """

    keyword = 'Token'
    token_related_model = None
    model = None

    def __init__(self):
        if not self.model:
            raise RuntimeError('`model` attribute must be be specified')
        if not self.token_related_model:
            raise RuntimeError('`token_related_model` attribute must be be specified')

        self.lowercase_keywork = self.keyword.lower()

    def authenticate(self, request):
        token = self.get_header_token(request)

        if not token:
            token = self.get_query_param_token(request)

        if not token:
            return None

        return self.authenticate_credentials(token)

    def get_header_token(self, request):
        auth_token = None
        header_auth = get_authorization_header(request).split()

        if header_auth and header_auth[0].lower() == self.lowercase_keywork.encode():
            if len(header_auth) == 1:
                msg = _('Invalid token header. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(header_auth) > 2:
                msg = _('Invalid token header. Token string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)

            try:
                auth_token = header_auth[1].decode()
            except UnicodeError:
                msg = _('Invalid token header. Token string should not contain invalid characters.')
                raise exceptions.AuthenticationFailed(msg)

        return auth_token

    def get_query_param_token(self, request):
        auth_token = request.query_params.get(self.lowercase_keywork, None)
        return auth_token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related(self.token_related_model).get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        user = getattr(token, self.token_related_model, None)
        if not user:
            raise exceptions.AuthenticationFailed(_('An unexpected error happened while authenticating.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        client = user.client

        return (user, client)


class UserTokenAuthentication(ClientTokenAuthentication):
    token_related_model = 'user'
    model = Token
