import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.project.models import Project, ProjectRole, Comment


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
