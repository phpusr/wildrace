from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


class IsAdminUserOrReadOnly(IsReadOnly):
    def has_permission(self, request, view):
        return bool(
            super().has_permission(request, view) or
            request.user and request.user.is_staff
        )
