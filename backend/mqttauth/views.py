from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from gatekeeper.models import Datastream
from gatekeeper.utils import parse_sta_url


# TODO: Should be moved to a custom user manager when we have one
def get_user_by_username_or_anonymous(username):
    user_class = get_user_model()
    try:
        return user_class.objects.get(username=username, is_active=True)
    except user_class.DoesNotExist:
        return user_class.get_anonymous()


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

    user = get_user_by_username_or_anonymous(request.POST.get('username'))

    if user.is_superuser:
        response_status_code = 200

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
        '1': 'subscribe_datastream',
        '2': 'publish_datastream',
    }

    permission_name = permission_name_map.get(acc)
    if not permission_name:
        return HttpResponse(status=response_status_code)

    user = get_user_by_username_or_anonymous(username)

    if user.is_superuser:
        return HttpResponse(status=200)

    parse_result = parse_sta_url(topic, prefix=settings.STA_VERSION)

    if parse_result['parts']:
        # For now we only look for a Datastream id and check permissions for that datastream
        for part in parse_result['parts']:
            if part['type'] == 'entity' and part['name'] == 'Datastream' and part['id']:
                try:
                    ds = Datastream.objects.get(sts_id=part['id'])

                    if user.has_perm(permission_name, ds):
                        response_status_code = 200
                except Datastream.DoesNotExist:
                    pass

    return HttpResponse(status=response_status_code)
