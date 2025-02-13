from rest_framework import serializers
from apps.project.models import Comment, Project, ProjectRole
from api.serializers.user import SimplifiedUserSerializer, UserSerializer


class ProjectRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectRole
        fields = ('id', 'role', 'user', 'user_id',)
        read_only_fields = ('project',)

class ProjectSerializer(serializers.ModelSerializer):
    member_roles = ProjectRoleSerializer(source='projectrole', many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'member_roles')


class ProjectUpdateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Project
        fields = ('title', 'description')
        extra_kwargs = {
            'title':{'required':False},
            'description':{'required':False},
        }

class CommentSerializer(serializers.ModelSerializer):
    user = SimplifiedUserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'project', 'user', 'content', 'created_at')
        read_only_fields = ('user',)

class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )

    class Meta:
        model = Comment
        fields = ('id', 'project', 'user', 'content', 'created_at')
