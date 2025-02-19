from rest_framework import permissions
from apps.project.models import Comment, ProjectRole


class IsEmailVerified(permissions.BasePermission):
    """
    Grants access only if user email is verfied. (not currently been used)
    """

    message = "Email verification is required to access this resource."

    def has_permission(self, request, view):
        # Allow access for schema generation (Swagger)
        if getattr(view, 'swagger_fake_view', False):
            return True  # Allows Swagger to generate docs without breaking

        # Check if the user is authenticated and their email is verified.
        return request.user.is_authenticated and request.user.email_verified

class IsProjectOwner(permissions.BasePermission):
    """
    Grants access only to project owners.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectRole.objects.filter(
            user=request.user, project=obj, role='OWNER'
        ).exists()

class IsProjectEditorOrHigher(permissions.BasePermission):
    """
    Grants access to project owners and editors.
    """

    def has_object_permission(self, request, view, obj):
        return ProjectRole.objects.filter(
            user=request.user, project=obj, role__in=['OWNER', 'EDITOR']
        ).exists()

class IsProjectMember(permissions.BasePermission):
    """
    Grants access to any user who has a role in the project.
    """
    
    def has_permission(self, request, view):
        # For api views that don't trigger 'has_object_permission' method
        return ProjectRole.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        print('Object:', obj)
        # Makes sure the user is a member of the specific project they are accessing 
        return ProjectRole.objects.filter(user=request.user, project=obj).exists()

class CanCommentOnProject(permissions.BasePermission):
    """
    Grants permission to comment if the user is a member of the project.
    """

    def has_permission(self, request, view):
        # Allow access for schema generation (Swagger)
        if getattr(view, 'swagger_fake_view', False):
            return True  # Allows Swagger to generate docs without breaking

        project_id = request.data.get("project")
        if not project_id:
            return False

        return ProjectRole.objects.filter(
            user=request.user, project_id=project_id, role__in=['OWNER', 'EDITOR']
        ).exists()


class CanUploadCommentDocument(permissions.BasePermission):
    """
    Grants permission to user that can upload comment document.
    """

    def has_permission(self, request, view):
        # Allow access for schema generation (Swagger)
        if getattr(view, 'swagger_fake_view', False):
            return True  # Allows Swagger to generate docs without breaking
        
        comment_id = request.data.get("comment")
        if not comment_id:
            return False

        comment_obj = Comment.objects.filter(id=comment_id).first()

        if comment_obj:
            # get the project instance from comment
            project = comment_obj.project

            return ProjectRole.objects.filter(
                user=request.user, project=project, role__in=['OWNER', 'EDITOR']
            ).exists()
        
        return False


class IsProjectOwnerOrCommentOwner(permissions.BasePermission):
    """
    Grants permission if user is the owner of the project or the creator of the comment
    """

    def has_object_permission(self, request, view, obj):
        # Get project instance from comment object
        project = obj.project
        
        if not project:
            return False

        return ProjectRole.objects.filter(
            user=request.user, project=project, role__in=['OWNER']
        ).exists() or obj.user == request.user
