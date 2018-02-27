import cgi
import logging
from wsgiref.util import is_hop_by_hop

import requests
from boltons.iterutils import remap
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from guardian.shortcuts import assign_perm
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Datastream, Thing
from .utils import get_gatekeeper_sta_prefix, get_object_by_self_link, parse_sta_url

logger = logging.getLogger(__name__)


def check_entity_permission(data, user):
    if isinstance(data, dict) and '@iot.selfLink' in data:
        obj = get_object_by_self_link(data['@iot.selfLink'])

        # TODO: What to do with unknown or missing items? Now they are just
        # removed them from the data.
        if not obj:
            return False

        # TODO: Cache permissions
        return user.has_perm('subscribe_{}'.format(obj._meta.model_name, obj))

    # No selfLink, include this dict
    return True


# TODO: Notice! Currently all Observations are excluded!
def exclude_unauthorized_data(data, user):
    def check_permission(visit_path, key, value):
        # For now let's just strip the counts because they could be wrong
        if isinstance(key, str) and '@iot.count' in key:
            return False

        return check_entity_permission(value, user)

    # First check the top-level object if there is one
    if not check_entity_permission(data, user):
        # TODO: Think about what to return
        return None

    # If the user had permission to the top-level item, check the sub entities
    return remap(data, visit=check_permission)


class Gatekeeper(APIView):
    """
    Gatekeeper between DataHubHel and STS

    # TODO: access control
    """
    sts_self_base_url = None
    sts_url = None
    sts_headers = {}
    sts_arguments = {}
    sts_content_type = ''

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        path = self.kwargs.pop('path')

        self.sts_self_base_url = request.build_absolute_uri(reverse('gatekeeper:index', kwargs={
            'path': ''
        })).rstrip('/')

        # TODO: validate path
        self.sts_url = '{}/{}'.format(settings.GATEKEEPER_STS_BASE_URL, path)

        self.sts_arguments['headers'] = self.filter_valid_sts_headers(request)
        self.sts_arguments['params'] = self.filter_valid_sts_arguments(request)

    def filter_valid_sts_headers(self, request):
        headers = {
            'Content-Type': request.META['CONTENT_TYPE'],
        }

        for header in request.META:
            if not header.startswith('HTTP_'):
                continue

            header_name = header[5:]
            if header_name not in ['ACCEPT', 'EXPECT', 'USER_AGENT']:
                continue

            headers[header_name] = request.META[header]
        return headers

    def filter_valid_sts_arguments(self, request):
        return {k: v for k, v in request.query_params.items() if k.startswith('$')}

    def get(self, request):
        return self.handle_request(request)

    def post(self, request):
        self.sts_arguments['json'] = self.request.data
        return self.handle_request(request)

    def put(self, request):
        self.sts_arguments['json'] = self.request.data
        return self.handle_request(request)

    def patch(self, request):
        self.sts_arguments['json'] = self.request.data
        return self.handle_request(request)

    def delete(self, request):
        return self.handle_request(request)

    def options(self, request, *args, **kwargs):
        return self.handle_request(request)

    def head(self, request):
        return self.handle_request(request)

    def create(self, request, sts_response):
        logger.info('User #{} created {}'.format(request.user.id, sts_response.headers['location']))

        # TODO: error checks
        entity_request = requests.get(self.local_url_to_sts(sts_response.headers['location']))

        created_object_data = entity_request.json()

        if '@iot.id' in created_object_data and '@iot.selfLink' in created_object_data:
            parse_result = parse_sta_url(created_object_data['@iot.selfLink'], prefix=get_gatekeeper_sta_prefix())

            # Save the created entity to the local database
            if parse_result['type'] == 'entity' and parse_result['parts'][-1]['name'] == 'Thing':
                instance = Thing.objects.create(
                    sts_id=created_object_data.get('@iot.id'),
                    name=created_object_data.get('name'),
                    description=created_object_data.get('description')
                )

                instance.user = request.user
                instance.save()

                # Query datastreams and save them to the database
                if 'Datastreams@iot.navigationLink' in created_object_data:
                    datastreams_url = self.local_url_to_sts(created_object_data['Datastreams@iot.navigationLink'])

                    # TODO: error checks
                    datastreams_request = requests.get(datastreams_url)
                    datastreams_data = datastreams_request.json()
                    if datastreams_data.get('@iot.count', 0) > 0 and 'value' in datastreams_data:
                        for ds in datastreams_data.get('value'):
                            logger.info(
                                'User #{} created {}'.format(request.user.id, ds.get('@iot.selflink')))

                            Datastream.objects.create(
                                sts_id=ds.get('@iot.id'),
                                name=ds.get('name'),
                                description=ds.get('description'),
                                user=request.user,
                                thing=instance,
                            )

            if parse_result['type'] == 'entity' and parse_result['parts'][-1]['name'] == 'Datastream':
                # Query the Thing this Datastream is a part of
                if 'Thing@iot.navigationLink' in created_object_data:
                    thing_url = self.local_url_to_sts(created_object_data['Thing@iot.navigationLink'])

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

                        instance.user = request.user
                        instance.save()

                        assign_perm('subscribe_datastream', request.user, instance)
                        assign_perm('publish_datastream', request.user, instance)

                    except Thing.DoesNotExist:
                        # TODO: handle error
                        pass

    def handle_request(self, request):
        sts_response = requests.request(request.method, self.sts_url, **self.sts_arguments)
        status_code = sts_response.status_code
        content_type = sts_response.headers['Content-Type'] if 'Content-Type' in sts_response.headers else ''
        response_args = {
            'content_type': content_type,
            'status': status_code,
        }

        json_content = None
        if cgi.parse_header(content_type)[0] == 'application/json':
            try:
                json_content = sts_response.json()
            except (JSONDecodeError, ValueError):
                pass

        if json_content:
            """
            Let DRF handle JSON responses and render them according to Django settings.
            This will allow the browsable API to be used.

            In the case where the content type is not of JSON type, use
            a HttpResponse to return the same kind of response as the
            STS returned.
            """

            # Pop the content type as we want to allow both JSON and browsable API responses
            response_args.pop('content_type')
            response_data = exclude_unauthorized_data(sts_response.json(), request.user)
            # TODO: Change the response if the user didn't have permission to read any of the records
            response = Response(data=response_data, **response_args)
        else:
            response = HttpResponse(content=sts_response.content, **response_args)

        if status_code == 404 or status_code >= 500:
            return response
        if status_code == 201 and 'location' in sts_response.headers:
            self.create(request, sts_response)

        headers = self.remap_response_headers(sts_response.headers)
        if headers:
            for name, value in headers.items():
                response[name] = value

        return response

    def remap_response_headers(self, headers):
        remapped_headers = {}

        for header_name in headers:
            if header_name.lower() in ['location', 'content-length'] or is_hop_by_hop(header_name):
                continue

            remapped_headers[header_name] = headers[header_name]

        return remapped_headers

    def local_url_to_sts(self, url):
        if not url.startswith('http'):
            return settings.GATEKEEPER_STS_BASE_URL + url

        if url.startswith(self.sts_self_base_url):
            return settings.GATEKEEPER_STS_BASE_URL + url[len(self.sts_self_base_url):]

        return url
