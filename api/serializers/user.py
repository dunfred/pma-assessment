from django.utils import timezone
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.models import User
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.serializers import PasswordField, TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'email_verified',
            'photo',
            'contact_number',
            'bio',
        ]

class SimplifiedUserSerializer(serializers.ModelSerializer):
    """Simplified User serializer"""

    class Meta:
        model = User
        fields = [
            'username',
            'photo',
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    """User Update serializer"""

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'photo',
            'contact_number',
            'bio',
        ]

        extra_kwargs = {
            'email': {'required':False},
            'username': {'required':False},
            'first_name': {'required':False},
            'last_name': {'required':False},
            'photo': {'required':False},
            'contact_number': {'required':False},
            'bio': {'required':False},
        }

class UserLoginSerializer(TokenObtainPairSerializer):
    """Login serializer for user"""

    def __init__(self, *args, **kwargs):
        """Overriding to change the error messages."""
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(
            error_messages={"blank": "Looks like you submitted wrong data. Please check and try again"}
        )
        self.fields['password'] = PasswordField(
            error_messages={"blank": "Looks like you submitted wrong data. Please check and try again"}
        )

    def validate(self, attrs):
        """Overriding response"""
        token_data = super().validate(attrs)

        data = {}
        data['tokens'] = {
            **token_data
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        token['username'] = user.username
        token['email'] = user.email
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # Standard refresh validation
        data = super().validate(attrs)
        # Extract the refresh token to get embedded claims
        refresh = RefreshToken(attrs['refresh'])
        
        # Update last_login for user
        try:
            user_id = refresh.payload.get('user_id')
            user = User.objects.filter(id=user_id).first()
            if user:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
        except Exception as e:
            # Log error if needed but don't interrupt the refresh process
            pass

        # Copy claims from refresh token to the new access token
        access_token = refresh.access_token
        access_token['username'] = refresh['username']
        access_token['email'] = refresh['email']
        access_token['email_verified'] = refresh['email_verified']

        # Return the new access token with claims
        data['access'] = str(access_token)
        return data

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for auth user registration."""
    first_name      = serializers.CharField(max_length=80, required=True)
    last_name       = serializers.CharField(max_length=80, required=True)
    contact_number  = serializers.CharField(max_length=15, required=False, help_text="Phone number in international format (+1234567890)",)
    password = serializers.CharField(max_length=255, required=True, style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'contact_number',
            'bio',
            'photo',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'contact_number': {'required': False},
            'bio': {'required': False},
            'photo': {'required': False},
        }

    def validate(self, attrs):
        """Validation for password."""
        try:
            password_validation.validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({'detail': str(e)})
        return attrs

    def create(self, validated_data):
        # Set username from the email
        validated_data['username'] = validated_data['email'].split('@')[0]
        return super().create(validated_data)


# Response Schema
class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class RegisteredUserResponseSerializer(serializers.Serializer):
    user = UserSerializer()  
    tokens = TokenResponseSerializer()
