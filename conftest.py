import uuid
import pytest
from apps.user.models import User
from rest_framework.test import APIClient
from apps.project.models import Project, ProjectRole
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    """Fixture to create a unique user with a given password."""
    def make_user(**kwargs):
        password = kwargs.pop("password", "password123")  # Use provided password or default
        unique_suffix = str(uuid.uuid4())[:8]  # Ensure username uniqueness
        defaults = {
            "email": f"testuser{unique_suffix}@example.com",
            "username": f"testuser{unique_suffix}",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "email_verified": True,
        }
        defaults.update(kwargs)
        user = User.objects.create_user(**defaults)
        user.set_password(password)  # Hash provided password correctly
        user.save()
        return user
    return make_user



@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def create_project(db, create_user):
    """Fixture to create a project and assign an owner."""
    def make_project(owner=None, title="Test Project", description="A sample project."):
        if owner is None:
            owner = create_user()
        project = Project.objects.create(title=title, description=description)
        ProjectRole.objects.create(user=owner, project=project, role="OWNER")
        return project, owner
    return make_project


@pytest.fixture
def authenticated_project_owner(api_client, create_project):
    """Fixture for an authenticated user who owns a project."""
    project, owner = create_project()
    refresh = RefreshToken.for_user(owner)
    access_token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    
    return api_client, owner, project  # Ensure tuple is returned

