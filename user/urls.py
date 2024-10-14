from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from django.urls import path

from user.views import UserCreateView, UserRetrieveUpdateView

app_name = 'user'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("create/", UserCreateView.as_view(), name="create_user"),
    path("me/", UserRetrieveUpdateView.as_view(), name="me"),
]
