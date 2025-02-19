from rest_framework import serializers
from apps.project.models import Comment, Document, Project, ProjectRole
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



class DocumentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )

    class Meta:
        model = Document
        fields = ['id', 'file', 'user', 'comment']
        
        kwargs = {
            'comment': {'write_only':True},
            'user': {'write_only':True},
        }

    def validate_file(self, value):
        min_size = 1024  # 1KB
        max_size = 5 * 1024 * 1024  # 5MB

        if value.size < min_size:
            raise serializers.ValidationError("File size must be at least 1KB.")
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 5MB.")

        return value

class CommentSerializer(serializers.ModelSerializer):
    user = SimplifiedUserSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'project', 'user', 'content', 'created_at', 'documents')
        read_only_fields = ('user',)

class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'project', 'user', 'content', 'documents', 'files')

    def validate_files(self, value):
        errors_list = []

        for file in value:
            min_size = 1024  # 1KB
            max_size = 5 * 1024 * 1024  # 5MB

            if file.size < min_size:
                errors_list.append({   
                    file.name: "File size must be at least 1KB."
                })
            if file.size > max_size:
                errors_list.append({   
                    file.name: "File size cannot exceed 5MB."
                })
        if errors_list:
            raise serializers.ValidationError(errors_list)

        return value

    def validate(self, attrs):
        # check if both content and files are empty
        if not attrs.get('content', False) and not attrs.get('files', False):
            raise serializers.ValidationError({'detail': 'Comment must have either content or file added.'})
        return attrs


    def create(self, validated_data):
        
        request = self.context['request']

        # return super().create(validated_data)
        files_data = validated_data.pop("files", [])
        comment = Comment.objects.create(**validated_data)

        # Save multiple files
        for file_data in files_data:
            Document.objects.create(comment=comment, user=request.user, file=file_data)

        return comment
