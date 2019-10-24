def get_user_id_from_request(request):
    user = getattr(request, 'user', None)
    return user.id if user and user.is_authenticated else None
