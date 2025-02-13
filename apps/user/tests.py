import pytest
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
class TestUserAPI:

    def test_user_registration(self, api_client):
        url = reverse("auth_register")
        payload = {
            "email": "newuser@example.com",
            "password": "StrongPassword123",
            "first_name": "New",
            "last_name": "User"
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data

    def test_user_login(self, create_user, api_client):
        user = create_user(password="StrongPassword123")
        url = reverse("auth_login")
        payload = {"email": user.email, "password": "StrongPassword123"}
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data["tokens"]

    def test_invalid_user_login(self, api_client):
        url = reverse("auth_login")
        payload = {"email": "wrong@example.com", "password": "wrongpass"}
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, create_user, api_client):
        user = create_user()
        refresh = RefreshToken.for_user(user)
        # Explicitly add extra claims to match CustomTokenRefreshSerializer
        refresh["username"] = user.username
        refresh["email"] = user.email
        refresh["email_verified"] = user.email_verified
        
        url = reverse("refresh-token")
        response = api_client.post(url, {"refresh": str(refresh)})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_user_logout(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("auth_logout")

        # Generate access token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set Authorization header manually
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Send logout request
        response = client.post(url)

        # Validate response
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out"

    def test_get_user_details(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("account_detail")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_user_update_patch(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("account_user_profile_update")
        payload = {"first_name": "Updated"}
        response = client.patch(url, payload)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"

    def test_user_update_put(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("account_user_profile_update")
        
        payload = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "bio": "This is a new bio."
        }
        
        response = client.put(url, payload)
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "UpdatedFirstName"
        assert user.last_name == "UpdatedLastName"
        assert user.bio == "This is a new bio."

    def test_user_logout_no_auth_header(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse("auth_logout")

        # Remove Authorization header
        client.credentials()

        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid token format"

    def test_user_logout_invalid_token_format(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse("auth_logout")

        # Set malformed Authorization header
        client.credentials(HTTP_AUTHORIZATION="InvalidTokenFormat")

        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid token format"

    def test_user_logout_no_active_sessions(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("auth_logout")

        # Generate access token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set Authorization header
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Manually remove refresh tokens
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        OutstandingToken.objects.filter(user=user).delete()

        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK  # The correct expected behavior
        assert response.data["detail"] == "No active sessions found"

    def test_user_logout_exception_handling(self, authenticated_client):
        client, user = authenticated_client
        url = reverse("auth_logout")
        
        # Generate access token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set Authorization header
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Simulate an unexpected exception (e.g., database error)
        with patch("rest_framework_simplejwt.token_blacklist.models.BlacklistedToken.objects.bulk_create", side_effect=Exception("DB error")):
            response = client.post(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "An error occurred while logging out" in response.data["detail"]
