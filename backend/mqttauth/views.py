from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from gatekeeper.models import Datastream
from gatekeeper.utils import parse_sta_url


@csrf_exempt
def auth(request):
    """Check username/password

    URI-Param           username   password    clientid    topic   acc
    http_getuser_uri    Y          Y           N           N       N
    """
    response_status_code = 403

    user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))

    # For now all registered users can connect
    if user:
        response_status_code = 200

    return HttpResponse(status=response_status_code)


@csrf_exempt
def superuser(request):
    """Check superuser

    URI-Param           username   password    clientid    topic   acc
    http_superuser_uri  Y          N           N           N       N
    """
    response_status_code = 403

    user_class = get_user_model()  # noqa
    try:
        user_class.objects.get(username=request.POST.get('username'), is_superuser=True, is_active=True)
        response_status_code = 200
    except user_class.DoesNotExist:
        pass

    return HttpResponse(status=response_status_code)


@csrf_exempt
def acl(request):
    """Check acl

    URI-Param           username   password    clientid    topic   acc
    http_aclcheck_uri   Y          N           Y           Y       Y
    """
    response_status_code = 403

    username = request.POST.get('username')
    topic = request.POST.get('topic')
    # client_id = request.POST.get('clientid')
    acc = request.POST.get('acc')  # 1 == sub, 2 == pub

    permission_name_map = {
        '1':  'subscribe_datastream',
        '2': 'publish_datastream',
    }

    permission_name = permission_name_map.get(acc)
    if not permission_name:
        return HttpResponse(status=response_status_code)

    # TODO: make prefix configurable
    parse_result = parse_sta_url(topic, prefix='v1.0')

    # For now we only look for a Datastream id and check permissions for that datastream
    for part in parse_result['parts']:
        if part['type'] == 'entity' and part['name'] == 'Datastream' and part['id']:
            try:
                ds = Datastream.objects.get(sts_id=part['id'])

                user_class = get_user_model()  # noqa
                try:
                    user = user_class.objects.get(username=username, is_active=True)

                    if user.has_perm(permission_name, ds):
                        response_status_code = 200
                except user_class.DoesNotExist:
                    pass
            except Datastream.DoesNotExist:
                pass

    return HttpResponse(status=response_status_code)
