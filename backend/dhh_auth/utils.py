from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def get_perm_obj(perm, obj_or_model=None):
    if isinstance(perm, Permission):
        return perm

    perm = perm.split('.')[-1]

    # Get object content
    if obj_or_model:
        ctype = ContentType.objects.get_for_model(obj_or_model)

    return Permission.objects.get(content_type=ctype, codename=perm)
