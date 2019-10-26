from datahubhel.dhh_auth.authentication import ClientTokenAuthentication
from datahubhel.service.models import ServiceToken


class ServiceTokenAuthentication(ClientTokenAuthentication):
    """
    Token authentication for user models with client support
    """

    keyword = 'ServiceToken'
    token_related_model = 'service'
    model = ServiceToken
