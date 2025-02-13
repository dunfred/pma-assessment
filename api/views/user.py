import logging
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from apps.user.models import User
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from api.utils.permissions import IsEmailVerified
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from api.serializers.user import (
    CustomTokenRefreshSerializer,
    RegisteredUserResponseSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

from api.utils.renderers import (
    LoginRenderer,
)

logger = logging.getLogger(__name__)

# Auth

@extend_schema_view(post=extend_schema(
    summary      = 'User Authentication',
    description  = "Get user's authentication code/token.",
    methods      = ['post'],
    operation_id = 'authLogin',
    tags         = ["Auth"],
))
class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer
    renderer_classes = [LoginRenderer]
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # If login was successful, update last_login
        if response.status_code == 200:
            # The user will be available in the serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            
            # Update last_login field only
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        return response


@extend_schema_view(post=extend_schema(
    summary      = 'Token Refresh',
    description  = 'Get a new Access Token using a Refresh Token.',
    methods      = ['post'],
    operation_id = 'authTokenRefresh',
    tags         = ["Auth"],
))
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


@extend_schema_view(post=extend_schema(
    summary      = 'Register User',
    description  = 'Register new user account.',
    methods      = ['post'],
    operation_id = 'userRegister',
    tags         = ["Auth"],
    responses=RegisteredUserResponseSerializer
))
class UserRegisterView(APIView):
    serializer_class = UserRegisterSerializer
    user_serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        ser = self.serializer_class(data=request.data)
        if ser.is_valid(raise_exception= True):
            user = ser.save()
            password = request.data["password"]

            user.set_password(password)
            user.is_active = True
            user.save()

            # This is where we send the user a verification mail with an otp code/link

            data = {}
            refresh = RefreshToken.for_user(user)
            data['user']        = self.user_serializer_class(user).data
            data['tokens'] = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            
            return Response(data, status=status.HTTP_201_CREATED)


@extend_schema_view(post=extend_schema(
    summary      = 'Logout User',
    description  = 'Delete or Invalidate server sessions/tokens for the logged in user.',
    methods      = ['post'],
    operation_id = 'userLogout',
    tags         = ["Auth"],
))
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the auth header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return Response({'detail': 'Invalid token format'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract the access token
            access_token_str = auth_header.split(' ')[1]
            
            try:
                # Parse the access token
                access_token = AccessToken(access_token_str)
                
                # Calculate token's remaining lifetime
                token_exp = datetime.fromtimestamp(access_token['exp'])
                remaining_time = (token_exp - datetime.now()).total_seconds()
                
                # Add the access token to cache blacklist
                if remaining_time > 0:
                    cache.set(f'blacklisted_token_{access_token_str}', 'blacklisted', timeout=int(remaining_time))
            
            except TokenError:
                pass  # Token might be invalid, continue with refresh token blacklisting
            
            # Blacklist all refresh tokens for the user
            refresh_tokens = OutstandingToken.objects.filter(
                user=request.user,
                blacklistedtoken__isnull=True
            )
            
            if not refresh_tokens:
                return Response({'detail': "No active sessions found"}, status=status.HTTP_200_OK)

            # Blacklist all refresh tokens
            BlacklistedToken.objects.bulk_create([
                BlacklistedToken(token=token)
                for token in refresh_tokens
            ])

            return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': f'An error occurred while logging out: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# User Account

@extend_schema_view(get=extend_schema(
    summary      = 'Account Details',
    description  = "Get account details of user or organization.",
    methods      = ['get'],
    operation_id = 'getUserDetails',
    tags         = ["Account"]
))
class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_object(self):
        user_id = self.request.user.id
        return generics.get_object_or_404(User, id=user_id)

@extend_schema_view(patch=extend_schema(
    summary      = 'Partial User Update',
    description  = "Partially update user account.",
    methods      = ['patch'],
    operation_id = 'updateUserAccountPatch',
    tags         = ["Account"],
    responses=UserSerializer,
    request=UserUpdateSerializer
))
@extend_schema_view(put=extend_schema(
    summary      = 'User Update',
    description  = "Update user account.",
    methods      = ['put'],
    operation_id = 'updateUserAccountPut',
    tags         = ["Account"],
    responses=UserSerializer,
    request=UserUpdateSerializer
))
class UserDetailUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmailVerified]

    def get_object(self):
        user_id = self.request.user.id
        return generics.get_object_or_404(User, id=user_id)

    def patch(self, request, *args, **kwargs):
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

        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Save the instance
        serializer.save()

        return Response(UserSerializer(instance).data, status=status.HTTP_200_OK)
