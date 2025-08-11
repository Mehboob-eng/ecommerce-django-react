from rest_framework.permissions import BasePermission

class IsStaffUser(BasePermission):
    """
    Allows access only to authenticated users who are staff.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
