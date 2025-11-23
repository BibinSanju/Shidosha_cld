"""
Custom permissions for courses app.
"""
from rest_framework import permissions


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow instructors to create/edit courses.
    Anyone can read (if published).
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for instructors and admins
        return (
            request.user.is_authenticated and
            request.user.role in ['INSTRUCTOR', 'ADMIN']
        )

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the course instructor or admin
        return (
            obj.instructor == request.user or
            request.user.is_staff
        )
