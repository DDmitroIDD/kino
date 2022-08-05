from rest_framework.permissions import BasePermission


class IsAnonymousUser(BasePermission):
    message = "You are already have an account"

    def has_permission(self, request, view):

        return request.user.is_anonymous


class IsAuthNotAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and not request.user.is_staff)
