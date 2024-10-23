from rest_framework.routers import SimpleRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from user.views import UserViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='users')

app_name = 'user'

urlpatterns = [
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path("", include(router.urls))
]

