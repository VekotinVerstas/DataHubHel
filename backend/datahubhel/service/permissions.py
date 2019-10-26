from rest_framework.permissions import SAFE_METHODS, BasePermission


class ServicePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method not in SAFE_METHODS and user not in obj.maintainers.all():
            return False

        return True
