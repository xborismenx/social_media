from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserCreateSerializer
    authentication_classes = ()

class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
