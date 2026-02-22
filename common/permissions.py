from rest_framework.permissions import BasePermission


class IsSystemAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_sysadmin)


class IsOwnerOrSystemAdmin(BasePermission):
    """
    Allows access to admin users or the owner of the object.
    The object must have a 'user' attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Admin has all access
        if request.user and request.user.is_sysadmin:
            return True

        # Instance must have an attribute named `user`
        return obj.user == request.user
