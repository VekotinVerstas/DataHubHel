import pytest
from .fixtures import *

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


def token_authenticate(api_client, user):
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client


@pytest.fixture
def api_user():
    user = get_user_model().objects.create(
        username='admin',
        first_name='First name',
        last_name='Last name'
    )
    return user


@pytest.fixture
def api_staff_client(api_user):
    api_client = APIClient()
    authenticated_client = token_authenticate(api_client, api_user)
    return authenticated_client
