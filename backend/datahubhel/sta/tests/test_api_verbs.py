import datetime
import pytest

from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED)

from datahubhel.sta.models import Observation


def _check_observation_properties_key(observation):
    required_observation_keys = {
        'id',
        'time',
        'sensor_id',
        'datastream',
        'property_name',
        'property_value',
    }
    assert set(observation.keys()) == required_observation_keys


@pytest.mark.django_db
def test_observation_list_returns_all_observations(
    observation_noise_level,
    observation_battery,
    api_staff_client
):
    url = reverse('sta:observation-list')
    response = api_staff_client.get(url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert len(json_response) == 2
    for resp in json_response:
        _check_observation_properties_key(resp)


@pytest.mark.django_db
def test_observation_detail_view_returns_observation_detail(
    observation_noise_level,
    api_staff_client,
    datastream_one
):
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': observation_noise_level.id}
    )
    response = api_staff_client.get(url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['id'] == '1234-XYZ-1234'
    assert json_response['property_name'] == 'noise_level'
    assert type(json_response['property_value']) == dict
    assert json_response['property_value'] == {"result": 23}
    assert json_response['datastream'] == datastream_one.id


@pytest.mark.django_db
def test_api_returns_404_status_for_non_existing_observation(
    api_staff_client,
    observation_noise_level
):
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': -1}
    )
    response = api_staff_client.get(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert Observation.objects.count() == 1


@pytest.mark.django_db
def test_endpoint_returns_all_observations_for_given_datastream(
    observation_noise_level,
    observation_battery,
    api_staff_client
):
    datastream_id =  observation_noise_level.datastream.id
    url = reverse(
        'sta:datastream-observation',
        kwargs={'datastream_id': datastream_id}
    )
    response = api_staff_client.get(url)
    json_response = response.json()[0]

    assert len(response.json()) == 1
    assert json_response['datastream'] == datastream_id
    assert json_response['datastream'] != observation_battery.datastream.id

    for each_observation in response.json():
        _check_observation_properties_key(each_observation)


@pytest.mark.django_db
def test_expanded_observation_returns_datastream_details(
    observation_noise_level,
    api_staff_client
):
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': observation_noise_level.id}
    )
    url = '?'.join((url, 'expand=Datastream'))
    response = api_staff_client.get(url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert type(json_response['datastream']) == dict
    assert sorted(json_response['datastream'].keys()) == sorted(['id', 'thing', 'sts_id', 'name', 'description', 'owner'])


@pytest.mark.django_db
def test_user_cannot_create_observation_even_with_correct_data(
    api_staff_client,
    datastream_two
):
    post_data = {
        'id': 'XYZ-XYZ-123',
        'time': str(datetime.datetime.now()),
        'sensor_id': 'ABC-XYZ-123',
        'property_value': {
            "distance": 49
        },
        'property_name': 'distance_travelled',
        'datastream': datastream_two.pk
    }
    url = reverse('sta:observation-list')
    response = api_staff_client.post(url, data=post_data, format='json')

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert Observation.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_patch_observation_even_with_correct_data(
    api_staff_client,
    observation_noise_level
):
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': observation_noise_level.id}
    )
    new_data = {'property_name': 'new_property'}

    response = api_staff_client.patch(url, data=new_data)

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_user_cannot_delete_observation(
    api_staff_client,
    observation_noise_level
):
    assert Observation.objects.count() == 1
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': observation_noise_level.id}
    )
    response = api_staff_client.delete(url)

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    assert Observation.objects.count() == 1


@pytest.mark.django_db
def test_api_returns_selected_fields_only_for_observation(
    api_staff_client,
    observation_noise_level
):
    selected_fields = ['id', 'time']
    selected_fields_str = ','.join(selected_fields)
    url = reverse(
        'sta:observation-detail',
        kwargs={'pk': observation_noise_level.id}
    )
    url = f"{url}?select={selected_fields_str}"
    response = api_staff_client.get(url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert set(json_response.keys()) == set(selected_fields)
    assert not 'sensor_id' in json_response


@pytest.mark.django_db
def test_user_cannot_post_observation_to_datastream(
    api_staff_client,
    datastream_two
):
    data_to_post = {
        'id': 'ABC-123',
        'time': str(datetime.datetime.now()),
        'sensor_id': '1',
        'property_name': 'prop',
        'property_value': {
            'prob_name': 'prop_value'
        }
    }

    url = reverse(
        'sta:datastream-observation',
        kwargs={'datastream_id': datastream_two.id}
    )
    response = api_staff_client.post(url, data=data_to_post, format='json')

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
