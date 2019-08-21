#!/usr/bin/env python3
from kafka_scripts import (
    create_ksql_streams,
    load_kafka_connectors,
    map_lat_lng_to_geopoints
)


def main():
    map_lat_lng_to_geopoints()
    create_ksql_streams()
    load_kafka_connectors()



if __name__ == '__main__':
    """
        This does the following stuffs:
        1. Maps lat, lng to geopoint in elasticsearch
        1. Creates the streams in the kafka
        2. Loads the connectors needed to connect kafka to
            elasticsearch, postgres database for sinking data.
        3. Starts the sample consumer that listens to OPEN311
            topic
    """
    main()
