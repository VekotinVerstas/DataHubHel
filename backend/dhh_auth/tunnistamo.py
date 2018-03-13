from rest_framework import exceptions as drf_excp

from .models import User


def resolve_user(request, payload):
    user = User.objects.filter(id=get_user_id(payload)).first()
    if not user:
        user = create_user_from_tunnistamo_data(payload)
    return user


def create_user_from_tunnistamo_data(payload):
    """
    Create UNSAVED User instance from JWT token payload.

    :type payload: Dict[str, Any]
    :rtype: User
    """
    return User(
        id=get_user_id(payload),
        first_name=payload.get('given_name'),
        last_name=payload.get('family_name'),
        email=payload.get('email'),
        is_staff=False,
        is_active=True,
        date_joined=None,
    )


def get_user_id(payload):
    user_id = payload.get('sub')
    if not user_id:
        raise drf_excp.AuthenticationFailed("Invalid JWT payload")
    return user_id
