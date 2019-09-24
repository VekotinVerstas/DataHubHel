import json
import requests

SINK_CONFIGURATION_FILES = [
    './kafka_scripts/postgres_sink.json',
    './kafka_scripts/min_sink.json',
    './kafka_scripts/elastic_sink.json',
    './kafka_scripts/elastic_sink_location.json',
]

CONNECT_SERVER = 'http://localhost:8083/connectors'


def _load_connector(file_to_load=""):
    assert file_to_load
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    with open(file_to_load) as f:
        data = json.load(f)
    response = requests.post(
        CONNECT_SERVER,
        headers=headers,
        data=json.dumps(data)
    )
    assert response.status_code == 201

    print (f"KAFKA_CONNECT: CONNECTOR {data['name']} LOADED")


def load_kafka_connectors():
    for file in SINK_CONFIGURATION_FILES:
        _load_connector(file)
