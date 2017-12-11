import re
from urllib.parse import urlparse

ENTITY_NAMES = [
    'Thing', 'Datastream', 'MultiDatastream', 'Sensor', 'Observation', 'ObservedProperty', 'FeatureOfInterest',
    'HistoricalLocation', 'Location'
]

ENTITY_NAMES_PLURAL_TO_SINGULAR_MAP = {
    'Things': 'Thing',
    'Datastreams': 'Datastream',
    'MultiDatastreams': 'MultiDatastream',
    'Sensors': 'Sensor',
    'Observations': 'Observation',
    'ObservedProperties': 'ObservedProperty',
    'FeaturesOfInterest': 'FeatureOfInterest',
    'HistoricalLocations': 'HistoricalLocation',
    'Locations': 'Location',
}


def parse_sta_url(url, prefix=None):
    """Parses a SensortThings API path and returns the type of the path and the entities and ids found

    examples:
    >>> parse_sta_url('/Things')
    {'type': 'collection', 'parts': [{'name': 'Thing', 'type': 'entity', 'id': None}]}

    >>> parse_sta_url('/v1.0/Datastreams(12345)', prefix='/v1.0')
    {'type': 'entity', 'parts': [{'name': 'Datastream', 'type': 'entity', 'id': '12345'}]}

    >>> parse_sta_url('/v1.0/Things(20)/Datastreams', prefix='/v1.0')
    {'type': 'collection', 'parts': [{'name': 'Thing', 'type': 'entity', 'id': '20'}, \
{'name': 'Datastream', 'type': 'entity', 'id': None}]}

    TODO: validate path. e.g.
    - entity names
    - property names
    - property part only after an entity
    """
    result = {
        'type': None,
        'parts': None,
    }

    url_components = urlparse(url)
    path = url_components.path

    if prefix and path.startswith(prefix):
        path = path[len(prefix):]

    parts = []
    for path_part in path.split('/'):
        if not path_part:
            continue

        matches = re.match(r'(?P<name>\w+)(?:\((?P<id>\d+)\))?', path_part)
        if matches is None:
            raise ValueError

        name = matches.group('name')
        if name in ENTITY_NAMES_PLURAL_TO_SINGULAR_MAP:
            name = ENTITY_NAMES_PLURAL_TO_SINGULAR_MAP[name]

        parts.append({
            'name': name,
            'type': 'entity' if name in ENTITY_NAMES else 'property',
            'id': matches.group('id') if matches.group('id') else None,
        })

    if not parts:
        return result

    result['parts'] = parts

    last_item = parts[-1]

    result['type'] = None
    if last_item['id']:
        result['type'] = 'entity'
    elif last_item['name'] in ENTITY_NAMES:
        result['type'] = 'collection'
    else:
        result['type'] = 'property'

    return result
