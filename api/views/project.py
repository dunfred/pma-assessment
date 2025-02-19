from rest_framework import status, generics, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from api.pagination import CommentsPagination, ProjectsPagination
from api.utils.renderers import get_standard_response
from apps.project.models import Comment, Project, ProjectRole
from rest_framework.permissions import IsAuthenticated
from api.serializers.project import CommentCreateSerializer, CommentSerializer, DocumentSerializer, ProjectRoleSerializer, ProjectSerializer, ProjectUpdateSerializer
from api.utils.permissions import (
    CanCommentOnProject,
    CanUploadCommentDocument,
    IsProjectEditorOrHigher,
    IsProjectMember,
    IsProjectOwner,
    IsProjectOwnerOrCommentOwner
)
from apps.user.models import User


# PROJECTS

@extend_schema_view(get=extend_schema(
    summary="List Projects",
    description="Retrieve a list of projects the authenticated user is a member of.",
    methods=['get'],
    operation_id='listProjects',
    tags=["Projects"],
    responses={
        200: get_standard_response(ProjectSerializer, many=True)
    }
))
class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectMember] # Any project memnber can view their projects
    pagination_class = ProjectsPagination

    def get_queryset(self):
        queryset = Project.objects.filter(projectrole__user=self.request.user).distinct()
        return queryset.order_by('-updated_at')


@extend_schema_view(post=extend_schema(
    summary="Create Project",
    description="Create a new project and assign the authenticated user as the owner.",
    methods=['post'],
    tags=["Projects"],
    request=ProjectSerializer,
    responses={201: get_standard_response(ProjectSerializer)}
))
class ProjectCreateAPIView(APIView):
    permission_classes = [IsAuthenticated] # All authenticated users can create projects

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            ProjectRole.objects.create(
                user=request.user,
                project=project,
                role='OWNER'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(get=extend_schema(
    summary="Retrieve Project",
    description="Retrieve details of a specific project.",
    methods=['get'],
    tags=["Projects"],
    responses={200: get_standard_response(ProjectSerializer)}
))
class ProjectDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsProjectMember] # Any project memnber can view a single project
    lookup_field = 'id'

    def get_object(self, id):
        proj =  Project.objects.filter(id=id, projectrole__user=self.request.user).first()
        
        if not proj:
            raise exceptions.NotFound('Project not found')
        
        # Manually trigger permission check
        self.check_object_permissions(self.request, proj)

        return proj

    def get(self, request, id):
        project = self.get_object(id)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)


@extend_schema_view(put=extend_schema(
    exclude=True
))
@extend_schema_view(patch=extend_schema(
    summary="Update Project",
    description='Update specific fields of an existing project.',
    methods=['patch'],
    operation_id='updateProject',
    tags=["Projects"],
    request=ProjectUpdateSerializer,
    responses= {200: get_standard_response(ProjectUpdateSerializer)}
))
class ProjectUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ProjectUpdateSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner] # Only owners can edit their project
    lookup_field = 'id'

    def get_queryset(self):
        return Project.objects.filter(projectrole__user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Loop through the fields in the validated data and update only those fields.
        for key, value in serializer.validated_data.items():
            # This will prevent fields been mistakenly overwritten with null values from validated data
            if value:
                setattr(instance, key, value)

        # Save the instance
        instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    delete=extend_schema(
        summary="Delete Project",
        description='Delete an existing project.',
        methods=['delete'],
        operation_id='deleteProject',
        tags=["Projects"],
        responses={204: "No Content"}
    )
)
class ProjectDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner] # Only owners can delete their project
    lookup_field = 'id'

    def get_queryset(self):
        return Project.objects.filter(projectrole__user=self.request.user)


@extend_schema_view(post=extend_schema(
    summary="Add Member to Project",
    description="Add a new member to a project. Only owners can add members.",
    methods=['post'],
    tags=["Project Members"],
    request=ProjectRoleSerializer,
    responses={201: "{'message': 'John successfully added to project Pseudo'}"}
))
class AddMemberAPIView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner] # Only owners can add members
    
    def post(self, request, id):
        project = get_object_or_404(Project, id=id)
        serializer = ProjectRoleSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not ProjectRole.objects.filter(user=request.user, project=project, role='OWNER').exists():
            return Response({'detail': 'Only owners can add members'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if ProjectRole.objects.filter(user=user, project=project).exists():
            return Response({'detail': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        ProjectRole.objects.create(user=user, project=project, role=serializer.validated_data['role'])
        return Response({'message': f'{user.username.title()} successfully added to project {project.title}'}, status=status.HTTP_201_CREATED)


@extend_schema_view(patch=extend_schema(
    summary="Update Member Role",
    description="Update a project member's role. Only owners can perform this action.",
    methods=['patch'],
    tags=["Project Members"],
    request=ProjectRoleSerializer,
    responses={200: "{'message': 'role updated'}"}
))
class UpdateMemberRoleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsProjectOwner]  # Only owners can update member roles
    
    def patch(self, request, id):
        try:
            project = Project.objects.get(id=id)
        except Project.DoesNotExist:
            project = None
            return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
            
        member_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not ProjectRole.objects.filter(user=request.user, project=project, role='OWNER').exists():
            return Response({'detail': 'Only owners can update member roles'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            member_role = ProjectRole.objects.get(project=project, user_id=member_id)
        except ProjectRole.DoesNotExist:
            member_role = None
            return Response({'detail': "User not a member of this project."}, status=status.HTTP_404_NOT_FOUND)

        member_role.role = new_role
        member_role.save()

        return Response({'message': 'role updated'}, status=status.HTTP_200_OK)


# COMMENTS

@extend_schema_view(get=extend_schema(
    summary="List Project Comments",
    description="Retrieve a list of comments under a project.",
    methods=['get'],
    tags=["Comments"],
    responses={200: get_standard_response(CommentSerializer, many=True)}
))
class CommentListAPIView(generics.ListAPIView):
    """
    API view to list comments under a project. Only members can view comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]
    pagination_class = CommentsPagination

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Comment.objects.filter(project_id=project_id).order_by('-created_at')


@extend_schema_view(post=extend_schema(
    summary="Create Comment",
    description="Create a new comment on a project. Only owners and editors can comment.",
    methods=['post'],
    tags=["Comments"],
    request=CommentCreateSerializer,
    responses={201: get_standard_response(CommentCreateSerializer)}
))
class CommentCreateAPIView(generics.CreateAPIView):
    """
    API view to create a new comment on a project.
    """
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated, CanCommentOnProject] # Only owners and editors can comment.


@extend_schema_view(get=extend_schema(
    summary="Retrieve Comment",
    description="Retrieve details of a specific comment.",
    methods=['get'],
    tags=["Comments"],
    responses={200: get_standard_response(CommentSerializer)}
))
class CommentDetailAPIView(generics.RetrieveAPIView):
    """
    API view to retrieve a specific comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(delete=extend_schema(
    summary="Delete Comment",
    description="Delete a specific comment.",
    methods=['delete'],
    tags=["Comments"],
    responses={204: "No Content"}
))
class CommentDeleteAPIView(generics.DestroyAPIView):
    """
    API view to delete a comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrCommentOwner] # Comment creator or project owner can delete a comment


# COMMENT DOCUMENTS
@extend_schema_view(post=extend_schema(
    summary="Upload Comment Document",
    description="Upload Comment Document",
    methods=['post'],
    tags=["Comments"],
    request=DocumentSerializer,
    responses={200: "{'message': 'document uploaded successfully'}"}
))
class UploadCommentDocumentAPIView(APIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, CanUploadCommentDocument]  # Only owners and editors can add documents to comments

    def post(self, request):
        ser = self.serializer_class(data=request.data, context={'request':request})

        if ser.is_valid(raise_exception=True):
            ser.save()
            return Response({'message': 'document uploaded successfully'}, status=status.HTTP_200_OK)



