from django.shortcuts import get_object_or_404
from rest_framework import permissions


class IsEmailVerified(permissions.BasePermission):
    message = "Email verification is required to access this resource."

    def has_permission(self, request, view):
        # Check if the user is authenticated and their email is verified.
        return request.user.is_authenticated and request.user.email_verified

class IsOwner(permissions.BasePermission):
    message = "You are not the creator of this project and do not have permission to access it."

    def has_object_permission(self, request, view, obj):
        # Check if the user is the creator of the election.
        return obj.created_by == request.user

