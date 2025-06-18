from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsTeacherOrReadOnly(BasePermission):
    message = 'Доступно только учителям. '

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )