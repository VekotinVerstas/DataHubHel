import json
import requests


def map_lat_lng_to_geopoints():
    """
    This is the template that needs to be in the
    elasticsearch before the indices are created.
    It basically tells the elasticsearch to treat
    the LOCATION field as geo_point and not array.
    """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    dynamic_template_mapping = {
            "index_patterns": "*",
            "settings": {
                "number_of_shards": 1
            },
            "mappings": {
                "dynamic_templates": [
                    {
                        "geopoint": {
                            "match": "*LOCATION",
                            "mapping": {
                                "type": "geo_point"
                            }
                        }
                    }
                ]
            }
        }
    response = requests.put(
        'http://localhost:9200/_template/geomapping',
        headers=headers,
        data=json.dumps(dynamic_template_mapping)
        )
    assert response.status_code == 200
    print('ELASTICSEARCH:: GEO_POINT MAPPING CREATED')
    return

