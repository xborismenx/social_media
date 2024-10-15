from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView, TokenBlacklistView,
)
from django.urls import path

from user.views import UserCreateView, UserRetrieveUpdateView, UserListView

app_name = 'user'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("all/", UserListView.as_view(), name="user_list"),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path("create/", UserCreateView.as_view(), name="create_user"),
    path("me/", UserRetrieveUpdateView.as_view(), name="me"),
]
