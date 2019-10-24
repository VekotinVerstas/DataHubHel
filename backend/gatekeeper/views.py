import cgi
import logging
import re
from json import JSONDecodeError
from wsgiref.util import is_hop_by_hop

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from datahubhel.dhh_auth.models import ClientPermission
from datahubhel.dhh_auth.utils import get_perm_obj

from datahubhel.core.models import Datastream, Thing
from .utils import ENTITY_TO_DATASTREAM_PATH, get_gatekeeper_sta_prefix, get_url_entity_type, parse_sta_url

logger = logging.getLogger(__name__)


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
    sts_extend_parameters = None

    # Matches on strings that, after the word Datastream, either end or continue with a comma
    sts_datastreams_extend_re = re.compile(r'.*Datastreams(,.*|$)')

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

    def create_thing(self, created_object_data):
        instance = Thing.objects.create(
            sts_id=created_object_data.get('@iot.id'),
            name=created_object_data.get('name'),
            description=created_object_data.get('description'),
            owner=self.request.user,
        )
        instance.save()

        # Query datastreams and save them to the database
        if 'Datastreams@iot.navigationLink' in created_object_data:
            datastreams_url = self.local_url_to_sts(created_object_data['Datastreams@iot.navigationLink'])

            # TODO: error checks
            datastreams_request = requests.get(datastreams_url)
            datastreams_data = datastreams_request.json()
            datastreams_value = datastreams_data.get('value', [])

            if len(datastreams_value) > 0:
                for ds in datastreams_value:
                    logger.info(
                        'User #{} created {}'.format(self.request.user.id, ds.get('@iot.selflink')))
                    Datastream.objects.create(
                        sts_id=ds.get('@iot.id'),
                        name=ds.get('name'),
                        description=ds.get('description'),
                        owner=self.request.user,
                        thing=instance,
                    )

    def create_datastream(self, created_object_data):
        # Query the Thing this Datastream is a part of
        if 'Thing@iot.navigationLink' in created_object_data:
            thing_url = self.local_url_to_sts(created_object_data['Thing@iot.navigationLink'])

            # TODO: error checks
            thing_request = requests.get(thing_url)
            thing_data = thing_request.json()

            try:
                thing = Thing.objects.get(sts_id=thing_data.get('@iot.id'))

                Datastream.objects.create(
                    sts_id=created_object_data.get('@iot.id'),
                    name=created_object_data.get('name'),
                    description=created_object_data.get('description'),
                    owner=self.request.user,
                    thing=thing,
                )

            except Thing.DoesNotExist:
                # TODO: handle error
                pass

    def create(self, request, sts_response):
        logger.info('User #{} created {}'.format(request.user.id, sts_response.headers['location']))

        # TODO: error checks
        entity_request = requests.get(self.local_url_to_sts(sts_response.headers['location']))

        created_object_data = entity_request.json()

        if '@iot.id' in created_object_data and '@iot.selfLink' in created_object_data:
            parse_result = parse_sta_url(created_object_data['@iot.selfLink'], prefix=get_gatekeeper_sta_prefix())

            if parse_result['type'] == 'entity':
                entity_type = parse_result['parts'][-1]['name'].lower()
                entity_create_function = getattr(self, 'create_' + entity_type, None)
                if entity_create_function:
                    entity_create_function(created_object_data)

    def expand_datastreams(self):
        """
        Expand the requested url to include datastreams

        As results are filtered by datastreams we want to
        gain access to all datastreams associated with the
        results. We do this by expanding the request to
        include datastreams.
        """

        params = self.sts_arguments.get('params', {})
        expand_query_param = params.get('$expand', '')

        # If we are already extending Datastreams there is no need for further actions
        if expand_query_param and self.sts_datastreams_extend_re.match(expand_query_param):
            return False

        parse_result = parse_sta_url(self.sts_url, prefix=get_gatekeeper_sta_prefix())

        entity_type = parse_result['parts'][-1]['name']
        if entity_type not in ENTITY_TO_DATASTREAM_PATH:
            return True

        expand_with = ENTITY_TO_DATASTREAM_PATH.get(entity_type)
        if not expand_with:
            return False

        self.sts_extend_parameters = expand_with

        if expand_query_param:
            self.sts_extend_parameters = ',{}'.format(expand_with)

        expand_params = '{}{}'.format(expand_query_param, self.sts_extend_parameters)

        self.sts_arguments['params']['$expand'] = expand_params

        return True

    def remove_internally_expanded_datastreams(self, data):
        """
        Remove expanded datastreams

        If the response was expanded to include datastreams
        but was not requested by the user, then remove the
        datastream values from the results.

        # TODO: Handle deep expand and only remove what was internally expanded
        # Example, user does $expand=Thing and internally we do $expand=Thing/Datastreams
        # then Thing should still stay expanded in the result but Datastreams should be
        # present.
        """
        if not self.sts_extend_parameters:
            return data

        datastream_lookup = self.sts_extend_parameters.split('/')[0]

        is_list = 'value' in data
        if is_list:
            for entry in data['value']:
                if datastream_lookup in entry:
                    del entry[datastream_lookup]
        elif datastream_lookup in data:
            del data[datastream_lookup]

        return data

    def sts_not_found(self):
        """
        To emulate STS as much as possible we respond
        in the same way as they do when nothing is found.
        """
        content = b'Nothing found.'

        # The STS server returns a json content type
        # even though the content is not json.
        headers = {
            'content_type': 'application/json;charset=UTF-8',
            'status': 404,
        }
        return HttpResponse(content=content, **headers)

    def get_datastreams_by_lookup(self, response, lookup_list, runid=1):
        if isinstance(response, list) and not lookup_list[0] == '':
            nested_entries = []
            for entry in response:
                runid += 1
                nested_entries += self.get_datastreams_by_lookup(entry, lookup_list, runid=runid)
            return self.get_datastreams_by_lookup(nested_entries, [''])

        if len(lookup_list) == 1:
            if lookup_list[0] == '':
                datastreams = response
            else:
                datastreams = response[lookup_list[0]]
            if not isinstance(datastreams, list):
                return [datastreams]
            return datastreams

        response = response[lookup_list[0]]
        return self.get_datastreams_by_lookup(response, lookup_list[1:])

    def get_permitted_datastreams(self, datastream_sts_ids):
        # Fetch all relevant datastream primary keys and sts ids
        datastream_info = Datastream.objects.filter(sts_id__in=datastream_sts_ids).values_list('pk', 'sts_id')
        # Create a dict from a list of tuples. [(1, 2), (3, 4)] -> {1: 2, 3: 4}
        datastream_map = dict((pk, int(sts_id)) for pk, sts_id in datastream_info)
        # Extract only the datastream ids to separate list
        datastream_ids = list(datastream_map.keys())

        # Get relevant permissions
        permission = get_perm_obj('view_datastream', Datastream)
        # Get all permissions filtered on the datastreams for the current client
        valid_permission_ids = (
            ClientPermission.objects
                .filter(permission=permission,
                        client=self.request.user.client,
                        content_type=permission.content_type,
                        object_pk__in=datastream_ids)
                .values_list('object_pk',
                             flat=True)
        )

        # Create a list of all of the sts ids that the client as permission to view
        # by mapping against the dict created earlier holding a id -> sts id mapping
        datastream_permissions = [datastream_map[int(valid_id)] for valid_id in valid_permission_ids]

        # Get all sts ids that the user is the owner, filtered by the relevant sts ids in the response
        if isinstance(self.request.user, get_user_model()):
            owned_datastreams = (
                Datastream.objects
                .filter(
                    thing__owner=self.request.user,
                    sts_id__in=datastream_sts_ids
                )
                .values_list(
                    'sts_id',
                    flat=True
                )
            )
            # Add the sts ids to the permission list
            datastream_permissions += [int(sts_id) for sts_id in owned_datastreams]

        return datastream_permissions

    def filter_response(self, response):  # noqa: C901
        """
        Filter response from STS server by filtering on the
        datastreams associated to the entries. Access control
        is checked by permission (all clients) or ownership
        (normal users only).

        Datastream permissions are fetched by first extracting
        all datastreams associated with the entries in the response
        after which these datastreams are queried and the internal
        as well as the sts id of the datastreams are extracted.
        All view_datastreams permissions given to the client for
        those datastreams is then queried. All entries are then
        filtered according to the view rights of the client.
        If the user is a normal user, i.e not a service, then
        ownership of the datastreams are also checked.

        If not results are left after the filtering, a ResponseNotFound
        exception is thrown to signal that a 404 result should
        be returned by the request handler.

        Caveat:
        When filtering a result containing only datastreams
        a special case is made as the result can not be
        expanded.

        TODO Clean up the function and lower its complexity
        """
        entity_type = get_url_entity_type(self.sts_url)
        if entity_type not in ENTITY_TO_DATASTREAM_PATH:
            return response

        if entity_type == 'MultiDatastream':
            raise Http404

        lookup_list = ENTITY_TO_DATASTREAM_PATH[entity_type].split('/')
        is_list = 'value' in response

        if not is_list:
            response_values = [response]
        else:
            response_values = response['value']

        # Create list of datastreams to fetch
        fetch_datastreams = []
        for entry in response_values:
            entry_datastreams = self.get_datastreams_by_lookup(entry, lookup_list)
            for datastream in entry_datastreams:
                if datastream['@iot.id'] not in fetch_datastreams:
                    fetch_datastreams.append(datastream['@iot.id'])

        permitted_datastreams = self.get_permitted_datastreams(fetch_datastreams)

        valid_values = []
        for entry in response_values:
            valid = False
            entry_datastreams = self.get_datastreams_by_lookup(entry, lookup_list)
            for datastream in entry_datastreams:
                if datastream['@iot.id'] in permitted_datastreams:
                    valid = True
            if valid:
                valid_values.append(entry)

        if not valid_values:
            raise Http404

        if not is_list:
            response = valid_values[0]
        else:
            response['value'] = valid_values

        return response

    def handle_request(self, request):  # noqa: C901
        if request.method == 'GET':
            self.expand_datastreams()

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

            response_data = json_content
            if request.method == 'GET':
                response_data = self.filter_response(response_data)
            response_data = self.remove_internally_expanded_datastreams(response_data)
            # TODO: Change the response if the user didn't have permission to read any of the records
            response = Response(data=response_data, **response_args)
        else:
            response = HttpResponse(content=sts_response.content, **response_args)

        if status_code == 404:
            raise Http404
        if status_code >= 500:
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
            if header_name.lower() in ['content-length'] or is_hop_by_hop(header_name):
                continue

            remapped_headers[header_name] = headers[header_name]

        return remapped_headers

    def local_url_to_sts(self, url):
        if not url.startswith('http'):
            return settings.GATEKEEPER_STS_BASE_URL + url

        if url.startswith(self.sts_self_base_url):
            return settings.GATEKEEPER_STS_BASE_URL + url[len(self.sts_self_base_url):]

        return url
