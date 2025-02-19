import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.project.models import Document, Project, ProjectRole, Comment


@pytest.mark.django_db
class TestProjectAPI:

    def test_list_projects(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("project-list")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["projects"]) == 1
        assert response.data["total_records"] == 1
        assert response.data["projects"][0]["title"] == project.title

    def test_create_project(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse("project-create")
        payload = {"title": "New Project", "description": "Project Description"}
        
        response = client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Project"

    def test_retrieve_project(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("project-detail", kwargs={"id": project.id})

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == project.title

    def test_update_project(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("project-update", kwargs={"id": project.id})

        payload = {"title": "Updated Title"}
        response = client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.title == "Updated Title"

    def test_delete_project(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("project-delete", kwargs={"id": project.id})

        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(id=project.id).exists()


@pytest.mark.django_db
class TestProjectMemberAPI:

    def test_add_member(self, authenticated_project_owner, create_user):
        client, _, project = authenticated_project_owner
        new_user = create_user()
        url = reverse("add-member", kwargs={"id": project.id})

        payload = {"user_id": new_user.id, "role": "EDITOR"}
        response = client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert ProjectRole.objects.filter(user=new_user, project=project, role="EDITOR").exists()

    def test_update_member_role(self, authenticated_project_owner, create_user):
        client, _, project = authenticated_project_owner
        new_user = create_user()
        
        # Add new member first
        ProjectRole.objects.create(user=new_user, project=project, role="EDITOR")

        url = reverse("update-member-role", kwargs={"id": project.id})
        payload = {"user_id": new_user.id, "role": "OWNER"}

        response = client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        project_role = ProjectRole.objects.get(user=new_user, project=project)
        assert project_role.role == "OWNER"

    def test_add_member_invalid_role(self, authenticated_project_owner, create_user):
        client, _, project = authenticated_project_owner
        new_user = create_user()
        url = reverse("add-member", kwargs={"id": project.id})

        payload = {"user_id": new_user.id, "role": "INVALID_ROLE"}

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "role" in response.data  # Invalid role should trigger serializer error

    def test_add_member_user_not_found(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("add-member", kwargs={"id": project.id})

        payload = {"user_id": 9999, "role": "EDITOR"}  # Nonexistent user ID

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "User not found"

    def test_add_member_user_not_a_member(self, authenticated_client, create_project, create_user):
        client, _ = authenticated_client  # Not the owner
        project, owner = create_project()
        new_user = create_user()
        url = reverse("add-member", kwargs={"id": project.id})

        payload = {"user_id": new_user.id, "role": "EDITOR"}

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN  # Only owners can add members

    def test_add_member_user_already_member(self, authenticated_project_owner, create_user):
        client, _, project = authenticated_project_owner
        existing_member = create_user()

        # Add the user as a member first
        ProjectRole.objects.create(user=existing_member, project=project, role="EDITOR")

        url = reverse("add-member", kwargs={"id": project.id})
        payload = {"user_id": existing_member.id, "role": "READER"}  # Trying to add again

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "User is already a member"

    def test_update_member_role_project_not_found(self, authenticated_project_owner):
        client, _, _ = authenticated_project_owner
        url = reverse("update-member-role", kwargs={"id": 9999})  # Nonexistent project

        payload = {"user_id": 1, "role": "EDITOR"}

        response = client.patch(url, payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "Project not found"

    def test_update_member_role_not_owner(self, authenticated_client, create_project, create_user):
        client, _ = authenticated_client  # Not the owner
        project, owner = create_project()
        new_user = create_user()
        ProjectRole.objects.create(user=new_user, project=project, role="EDITOR")

        url = reverse("update-member-role", kwargs={"id": project.id})
        payload = {"user_id": new_user.id, "role": "OWNER"}

        response = client.patch(url, payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == "Only owners can update member roles"



@pytest.mark.django_db
class TestProjectCommentsAPI:

    def test_list_comments(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("comment-list", kwargs={"project_id": project.id})

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["comments"]) == 0
        assert response.data["total_records"] == 0

    def test_create_comment(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("comment-create")

        payload = {"project": project.id, "content": "This is a test comment"}
        response = client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "This is a test comment"

    def test_delete_comment(self, authenticated_project_owner):
        client, user, project = authenticated_project_owner
        comment = Comment.objects.create(project=project, user=user, content="Test Comment")
        url = reverse("comment-delete", kwargs={"pk": comment.id})

        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()
    
    def test_delete_comment_not_found(self, authenticated_project_owner):
        client, user, project = authenticated_project_owner

        url = reverse("comment-delete", kwargs={"pk": 0}) # Non-existent id

        response = client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No Comment matches the given query."

    def test_upload_valid_document(self, authenticated_comment_owner, valid_file):
        client, _, comment = authenticated_comment_owner
        url = reverse("comment-document-upload")
        
        payload = {'file': valid_file, 'comment': 1}  # Ensure a valid comment ID exists
        response = client.post(url, payload, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'document uploaded successfully'
        assert Document.objects.filter(comment=comment).count() == 1

    def test_upload_invalid_file_size_small(self, authenticated_comment_owner, small_file):
        client, _, comment = authenticated_comment_owner
        url = reverse("comment-document-upload")

        payload = {'file': small_file, 'comment': 1}
        response = client.post(url, payload, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'File size must be at least 1KB' in str(response.data)

    def test_upload_invalid_file_size_large(self, authenticated_comment_owner, large_file):
        client, _, comment = authenticated_comment_owner
        url = reverse("comment-document-upload")

        payload = {'file': large_file, 'comment': 1}
        response = client.post(url, payload, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'File size cannot exceed 5MB' in str(response.data)

    def test_unauthenticated_user_cannot_upload(self, api_client, create_project, valid_file):
        # Create a project
        project, owner = create_project()

        # Add comment to the project
        comment = Comment.objects.create(content="Tommy Lee", user=owner, project=project)

        url = reverse("comment-document-upload")

        payload = {'file': valid_file, 'comment': comment.pk}
        response = api_client.post(url, payload, format='multipart')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_comment_with_multiple_files(self, authenticated_project_owner, valid_file, small_file, large_file):
        client, _, project = authenticated_project_owner
        url = reverse("comment-create")
        
        payload = {'project': 1, 'content': 'This is a test comment', 'files': [valid_file, small_file, large_file]}
        response = client.post(url, payload, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['validations']['files'][large_file.name]) == 'File size cannot exceed 5MB.'
        assert str(response.data['validations']['files'][small_file.name]) == 'File size must be at least 1KB.'

    def test_create_comment_with_content_or_document(self, authenticated_project_owner, valid_file):
        client, _, project = authenticated_project_owner
        url = reverse("comment-create")
        
        # Create comment with content only
        payload_content_only = {'project': 1, 'content': 'This is a test comment'}
        response_content = client.post(url, payload_content_only)
        assert response_content.status_code == status.HTTP_201_CREATED
        
        # Create comment with files only
        payload_document_only = {'project': 1, 'files': [valid_file]}
        response_document = client.post(url, payload_document_only, format='multipart')
        assert response_document.status_code == status.HTTP_201_CREATED
        
        # Create comment without both content and files
        payload_both_missing = {'project': 1}
        response_both_missing = client.post(url, payload_both_missing, format='multipart')
        assert response_both_missing.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_with_content_and_document(self, authenticated_project_owner, valid_file):
        client, _, project = authenticated_project_owner
        url = reverse("comment-create")
        
        # Create comment with both content and files
        payload_both = {'project': project.pk, 'content': 'This is a another test comment', 'files': [valid_file]}
        response_both = client.post(url, payload_both, format='multipart')
        assert response_both.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
class TestProjectEdgeCases:
    
    def test_create_project_invalid_data(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse("project-create")

        payload = {}  # Missing required fields

        response = client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data  # Title is required
        assert "description" in response.data  # Description is required
        
    def test_retrieve_project_not_found(self, authenticated_project_owner):
        client, _, project = authenticated_project_owner
        url = reverse("project-detail", kwargs={"id": 0}) # Non-existent ID passed

        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "Project not found"

    def test_delete_project(self, authenticated_project_owner):
        client, owner, project = authenticated_project_owner  # Authenticated as owner
        url = reverse("project-delete", kwargs={"id": project.id})

        response = client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(id=project.id).exists()

    def test_add_member_unauthorized(self, authenticated_client, create_project, create_user):
        client, _ = authenticated_client
        project, _ = create_project()
        new_user = create_user()
        url = reverse("add-member", kwargs={"id": project.id})

        payload = {"user_id": new_user.id, "role": "EDITOR"}
        response = client.post(url, payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN  # Only owners can add members

    def test_update_member_role_invalid(self, authenticated_project_owner, create_user):
        client, _, project = authenticated_project_owner
        non_member = create_user()

        url = reverse("update-member-role", kwargs={"id": project.id})
        payload = {"user_id": non_member.id, "role": "OWNER"}

        response = client.patch(url, payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND  # Cannot update a non-member
