import cgi
import json
from collections import OrderedDict

import requests
from boltons.iterutils import remap
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import (
    BasicAuthentication, SessionAuthentication)
from rest_framework.decorators import authentication_classes

from gatekeeper.models import Datastream, Thing
from gatekeeper.utils import parse_sta_url


@csrf_exempt
@authentication_classes((SessionAuthentication, BasicAuthentication))
def index(request, path):
    """This is a quick and dirty proof of concept for proxying the SensorThings API queries to the real STA server.

    Additionally when creating Things or Datastreams, this view will create instances for them in the local database.
    """
    user = request.user
    self_base_url = request.build_absolute_uri(reverse('gatekeeper:index', kwargs={
        'path': ''
    })).rstrip('/')

    # TODO: validate path
    url = '{}/{}'.format(settings.GATEKEEPER_STS_BASE_URL, path)

    request_arguments = {
        'headers': {
            'Content-Type': request.META['CONTENT_TYPE'],
        },
    }

    for header in request.META:
        if not header.startswith('HTTP_'):
            continue

        header_name = header[5:]
        if header_name not in ['ACCEPT', 'EXPECT', 'USER_AGENT']:
            continue

        request_arguments['headers'][header_name] = request.META[header]

    # TODO: access control
    if request.method == 'GET':
        # TODO: validate GET parameters
        request_arguments['params'] = request.GET
    elif request.method in ['POST', 'PUT', 'PATCH']:
        # if not user.is_authenticated:
        #     raise PermissionDenied

        request_arguments['data'] = request.body

    # TODO: error checks
    r = requests.request(request.method, url, **request_arguments)

    if r.status_code == 201 and 'location' in r.headers:
        # TODO: error checks
        entity_request = requests.get(r.headers['location'])
        created_object_data = entity_request.json()

        if '@iot.id' in created_object_data and '@iot.selfLink' in created_object_data:
            self_link = created_object_data['@iot.selfLink'].replace(
                settings.GATEKEEPER_STS_BASE_URL, self_base_url)

            # TODO: make prefix configurable
            parse_result = parse_sta_url(self_link, prefix='/api/v1.0')

            # Save the created entity to the local database
            if parse_result['type'] == 'entity' and parse_result['parts'][-1]['name'] == 'Thing':
                instance = Thing.objects.create(
                    sts_id=created_object_data.get('@iot.id'),
                    name=created_object_data.get('name'),
                    description=created_object_data.get('description')
                )

                if user.is_authenticated:
                    instance.user = user
                    instance.save()

                # Query datastreams and save them to the database
                if 'Datastreams@iot.navigationLink' in created_object_data:
                    # TODO: make version prefix configurable
                    datastreams_url = '{}/v1.0/{}'.format(settings.GATEKEEPER_STS_BASE_URL,
                                                          created_object_data['Datastreams@iot.navigationLink'])
                    # TODO: error checks
                    datastreams_request = requests.get(datastreams_url)
                    datastreams_data = datastreams_request.json()
                    if datastreams_data.get('@iot.count', 0) > 0 and 'value' in datastreams_data:
                        for ds in datastreams_data.get('value'):
                            Datastream.objects.create(
                                sts_id=ds.get('@iot.id'),
                                name=ds.get('name'),
                                description=ds.get('description'),
                                user=user if user.is_authenticated else None,
                                thing=instance,
                            )

            if parse_result['type'] == 'entity' and parse_result['parts'][-1]['name'] == 'Datastream':
                # Query the Thing this Datastream is a part of
                if 'Thing@iot.navigationLink' in created_object_data:
                    # TODO: make version prefix configurable
                    thing_url = '{}/v1.0/{}'.format(settings.GATEKEEPER_STS_BASE_URL,
                                                    created_object_data['Thing@iot.navigationLink'])
                    # TODO: error checks
                    thing_request = requests.get(thing_url)
                    thing_data = thing_request.json()

                    try:
                        thing = Thing.objects.get(sts_id=thing_data.get('@iot.id'))

                        instance = Datastream()
                        instance.thing = thing
                        instance.sts_id = created_object_data.get('@iot.id')
                        instance.name = created_object_data.get('name')
                        instance.description = created_object_data.get('description')

                        if user.is_authenticated:
                            instance.user = user

                        instance.save()

                    except Thing.DoesNotExist:
                        # TODO: handle error
                        pass

    content = r.content
    content_type = r.headers['Content-Type'] if 'Content-Type' in r.headers else ''

    # If the content is JSON fix the urls to point to this view, not directly to the STS
    # (Filter 404 out because FraunhoferIOSB/SensorThingsServer will return 404 with the
    # content type application/json with the content "Nothing found".)
    if cgi.parse_header(content_type)[0] == 'application/json' and r.status_code != 404:
        data = json.loads(content, object_pairs_hook=OrderedDict, encoding=r.encoding)

        def fix_urls(visit_path, key, value):
            if isinstance(key, str) and any([k in key for k in ['url', 'Link']]):
                return key, value.replace(settings.GATEKEEPER_STS_BASE_URL, self_base_url)

            return key, value

        data = remap(data, visit=fix_urls)

        content = json.dumps(data, indent=4, ensure_ascii=False)

    response = HttpResponse(status=r.status_code, reason=r.reason, content_type=content_type, content=content)

    for header_name in r.headers:
        if header_name.lower() in ['location', 'content-length', 'transfer-encoding']:
            continue

        response[header_name] = r.headers[header_name]

    # Rewrite location header url
    if 'location' in r.headers and r.headers['location'].startswith(settings.GATEKEEPER_STS_BASE_URL):
        response['Location'] = r.headers['location'].replace(settings.GATEKEEPER_STS_BASE_URL, self_base_url)

    return response
