from django.urls import path

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

]
