import json
import random
import time
from datetime import datetime, timezone
from functools import lru_cache
from typing import Callable, Generator, Optional

import confluent_kafka.avro
from django.conf import settings

GATEWAY_ID: int = (
    getattr(settings, 'GATEWAY_ID', random.randint(2**31, 2**32 - 1)))

_id_counter: int = 0


def _time_ns(_time: Callable[[], float] = time.time) -> int:
    """
    Get current time since 1970-01-01T00:00:00Z as nanoseconds.

    Emulates time.time_ns which exists on Python 3.7 or newer.
    """
    return int(_time() * 1_000_000_000.0)


time_ns: Callable[[], int]
try:
    from time import time_ns  # type: ignore
except ImportError:
    time_ns = _time_ns


def generate_id(time_ns: Callable[[], int] = time_ns) -> str:
    """
    Generate a single id for observation.

    The returned id is a concatenation of a timestamp, gateway id and a
    counter, which wraps at 65536.
    """
    now = time_ns()
    global _id_counter
    _id_counter = (_id_counter + 1) & 0xffff  # take the 16 lowest bits
    return '{:016x}{:08x}{:04x}'.format(now, GATEWAY_ID, _id_counter)


def generate_ids(
        time_ns: Callable[[], int] = time_ns,
) -> Generator[str, None, None]:
    """
    Generate a sequence of ids for a set of observations.

    Each id is a concatenation of a timestamp, gateway id and a counter,
    which wraps at 65536.  This function uses the same timestamp for
    each generated id, so the returned ids are no longer unique when the
    counter wraps, i.e. if more than 65536 ids are generated.
    """
    now = time_ns()
    prefix = '{:016x}{:08x}'.format(now, GATEWAY_ID)
    global _id_counter
    while True:
        _id_counter = (_id_counter + 1) & 0xffff  # take the 16 lowest bits
        yield prefix + '{:04x}'.format(_id_counter)


def make_ms_timestamp(dt: Optional[datetime]) -> Optional[int]:
    """
    Convert a datetime object to a millisecond precision timestamp.
    """
    if dt is None:
        return None
    return int((dt - EPOCH).total_seconds() * 1000)


EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)


@lru_cache()
def get_kafka_producer() -> confluent_kafka.avro.AvroProducer:
    """
    Get a producer for sending the observations to Kafka.
    """
    key_schema = confluent_kafka.avro.loads('"string"')
    value_schema = confluent_kafka.avro.loads(json.dumps({
        "namespace": "fi.fvh.datahubhel",
        "name": "Observation",
        "type": "record",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "time", "type": ["null", "long"],
             "logicalType": "timestamp-millis"},
            {"name": "name", "type": "string"},
            {"name": "value", "type": "string"}
        ]
    }))

    return confluent_kafka.avro.AvroProducer({
        'bootstrap.servers': 'localhost:29092',
        'schema.registry.url': 'http://localhost:8081'
    }, default_key_schema=key_schema, default_value_schema=value_schema)
