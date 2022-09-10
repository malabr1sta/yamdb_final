from rest_framework import permissions


class Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            (request.user.is_authenticated
             and request.user.role == 'admin')
            or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return (request.user.role == 'admin' or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin' or request.user.is_superuser)
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdminModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_authenticated
                    or request.user.role == 'admin'
                    or request.user.is_superuser
                    or request.user.role == 'moderator')
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or (
                (request.user.role == 'admin'
                 or request.user.is_superuser
                 or request.user.role == 'moderator')
                and request.method != 'POST')
        )
