# type: ignore

from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    - Read permissions (GET, HEAD, OPTIONS) allowed for any request
    - Write permissions (PUT, PATCH, DELETE) only allowed for the author
    
    Used for Post and Comment models where only the creator
    should be able to modify or delete their content.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Similar to IsAuthorOrReadOnly but uses 'owner' field.
    Useful for models that use 'owner' instead of 'author'.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # check for 'owner' or 'user' field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False
