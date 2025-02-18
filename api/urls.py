from django.urls import path

from api.views.project import (
    AddMemberAPIView,
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentDetailAPIView,
    CommentListAPIView,
    ProjectCreateAPIView,
    ProjectDetailAPIView,
    ProjectListAPIView,
    ProjectUpdateAPIView,
    ProjectDeleteAPIView,
    UpdateMemberRoleAPIView,
    UploadCommentDocumentAPIView
)
from api.views.user import (
    UserDetail,
    UserLoginView,
    UserLogoutView,
    UserDetailUpdateView,
    UserRegisterView,
    CustomTokenRefreshView,
)


urlpatterns = [
    # Auth
    path('auth/login/', UserLoginView.as_view(), name='auth_login'),
    path("auth/token/refresh/",  CustomTokenRefreshView.as_view(), name="refresh-token"),
    path('auth/register/', UserRegisterView.as_view(), name='auth_register'),
    path('auth/logout/', UserLogoutView.as_view(), name='auth_logout'),

    # Account
    path('accounts/profile/',            UserDetail.as_view(), name='account_detail'),
    path('accounts/profile/user/update/',UserDetailUpdateView.as_view(), name='account_user_profile_update'),


    # Project
    path('projects/', ProjectListAPIView.as_view(), name='project-list'),
    path('projects/create/', ProjectCreateAPIView.as_view(), name='project-create'),
    path('projects/<int:id>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    path('projects/<int:id>/update/', ProjectUpdateAPIView.as_view(), name='project-update'),
    path('projects/<int:id>/delete/', ProjectDeleteAPIView.as_view(), name='project-delete'),
    path('projects/<int:id>/add-member/', AddMemberAPIView.as_view(), name='add-member'),
    path('projects/<int:id>/update-member-role/', UpdateMemberRoleAPIView.as_view(), name='update-member-role'),
    
    # Comments
    path('projects/<int:project_id>/comments/', CommentListAPIView.as_view(), name='comment-list'),
    path('comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/delete/', CommentDeleteAPIView.as_view(), name='comment-delete'),
    
    # Documents
    path('comments/documents/create/', UploadCommentDocumentAPIView.as_view(), name='comment-document-upload'),
    
]
