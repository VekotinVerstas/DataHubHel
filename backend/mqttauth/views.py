import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from dhh_auth.models import ClientPermission
from dhh_auth.utils import get_perm_obj
from gatekeeper.models import Datastream
from gatekeeper.utils import parse_sta_url
from service.models import Service, ServiceToken

logger = logging.getLogger(__name__)


@csrf_exempt
def auth(request):
    """Check username/password

    URI-Param           username   password    clientid    topic   acc
    http_getuser_uri    Y          Y           N           N       N
    """
    response_status_code = status.HTTP_403_FORBIDDEN

    try:
        ServiceToken.objects.get(service__identifier=request.POST.get('username'), service__is_active=True,
                                 key=request.POST.get('password'))

        response_status_code = status.HTTP_200_OK
    except ServiceToken.DoesNotExist:
        pass

    logger.info('MQTT authentication for service "{}" {}'.format(
        request.POST.get('username'), 'succeeded' if response_status_code == status.HTTP_200_OK else 'failed'))

    return HttpResponse(status=response_status_code)


@csrf_exempt
def superuser(request):
    """Check if the user with the supplied username is a superuser

    Excludes any username that is an identifier of a service because
    they could be mixed up and could end in a privilege escalation.

    URI-Param           username   password    clientid    topic   acc
    http_superuser_uri  Y          N           N           N       N
    """
    response_status_code = status.HTTP_403_FORBIDDEN

    username = request.POST.get('username')
    user = None

    user_class = get_user_model()
    try:
        service_identifiers = Service.objects.all().values_list('identifier', flat=True)
        user = user_class.objects.exclude(username__in=service_identifiers).get(username=username, is_active=True)
    except user_class.DoesNotExist:
        pass

    if user and user.is_superuser:
        response_status_code = status.HTTP_200_OK

    logger.info('MQTT is super user check for user "{}": {}'.format(
        username, 'True' if response_status_code == status.HTTP_200_OK else 'False'))

    return HttpResponse(status=response_status_code)


@csrf_exempt
def acl(request):
    """Check acl

    URI-Param           username   password    clientid    topic   acc
    http_aclcheck_uri   Y          N           Y           Y       Y
    """
    response_status_code = status.HTTP_403_FORBIDDEN

    username = request.POST.get('username')
    topic = request.POST.get('topic')
    # client_id = request.POST.get('clientid')
    acc = request.POST.get('acc')  # 1 == sub, 2 == pub

    permission_name_map = {
        '1': 'view_datastream',
        '2': 'create_observation',
    }

    permission_name = permission_name_map.get(acc)
    if not permission_name:
        logger.info('MQTT ACL check encountered unknown value for acc: "{}"'.format(acc))
        return HttpResponse(status=response_status_code)

    log_text = 'MQTT ACL check for service "{}", topic "{}", perm "{}". Result: '.format(
        username, topic, permission_name)

    try:
        service = Service.objects.get(identifier=username)
    except Service.DoesNotExist:
        logger.info(log_text + 'Unknown service.')
        return HttpResponse(status=response_status_code)

    parse_result = parse_sta_url(topic, prefix=settings.STA_VERSION)

    if parse_result and parse_result['parts']:
        # For now we only look for a Datastream id and check permissions for that datastream
        for part in parse_result['parts']:
            if part['type'] == 'entity' and part['name'] == 'Datastream' and part['id']:
                try:
                    ds = Datastream.objects.get(sts_id=part['id'])
                    permission = get_perm_obj(permission_name, Datastream)

                    ClientPermission.objects.get(permission=permission, client=service.client,
                                                 content_type=permission.content_type, object_pk=ds.id)

                    response_status_code = status.HTTP_200_OK
                except (Datastream.DoesNotExist, ClientPermission.DoesNotExist):
                    pass

    logger.info(log_text + ('Access granted' if response_status_code == status.HTTP_200_OK else 'Access denied'))

    return HttpResponse(status=response_status_code)
