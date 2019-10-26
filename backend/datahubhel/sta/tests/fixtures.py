import datetime
import pytest

from django.contrib.auth import get_user_model

from gatekeeper.models import Datastream, EntityBase, Thing
from datahubhel.sta.models import Observation


@pytest.fixture()
@pytest.mark.django_db()
def user():
    fixture_user = get_user_model().objects.create(
        username='user-one',
        first_name='Firstname',
        last_name='Lastname'
    )
    return fixture_user


@pytest.fixture()
@pytest.mark.django_db()
def thing(user):
    sensor_thing = Thing.objects.create(
        owner=user,
        sts_id=1,
        name='Entity base one',
        description='EB description'
    )
    return sensor_thing


@pytest.fixture()
@pytest.mark.django_db()
def datastream_one(thing):
    dstream = Datastream.objects.create(
        thing=thing,
        sts_id=1,
        name='Datastream1'
    )
    return dstream


@pytest.fixture()
@pytest.mark.django_db()
def datastream_two(thing):
    dstream = Datastream.objects.create(
        thing=thing,
        sts_id=2,
        name='Datastream2'
    )
    return dstream


@pytest.fixture()
@pytest.mark.django_db()
def observation_noise_level(datastream_one):
    observation = Observation.objects.create(
        id='1234-XYZ-1234',
        time=datetime.datetime.now(),
        sensor_id=1,
        property_name='noise_level',
        property_value={"result": 23},
        datastream=datastream_one
    )
    return observation


@pytest.fixture()
@pytest.mark.django_db()
def observation_battery(datastream_two):
    observation = Observation.objects.create(
        id='1234-ABC-1234',
        time=datetime.datetime.now(),
        sensor_id=1,
        property_name='battery',
        property_value={"result": False},
        datastream=datastream_two
    )
    return observation
