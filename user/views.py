from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from user.models import Follow, User
from user.serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [IsAuthenticated()]

    def get_authentication_classes(self):
        if self.action == 'create':
            return []
        return [JWTAuthentication]

    @action(detail=False, methods=['GET', "POST"], url_path='me')
    def me(self, request):
        """returns the data of the current authenticated user"""
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def follow(self, request, pk=None):
        user_to_follow = get_object_or_404(User, pk=pk)
        current_user = request.user

        if user_to_follow == current_user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(follower=current_user, following=user_to_follow).exists():
            return Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(follower=current_user, following=user_to_follow)
        return Response({"success": f"You are now following {user_to_follow.username}."},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = get_object_or_404(User, pk=pk)
        current_user = request.user

        if user_to_unfollow == current_user:
            return Response({"error": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance = Follow.objects.filter(follower=current_user, following=user_to_unfollow).first()
        if not follow_instance:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance.delete()
        return Response({"success": f"You have unfollowed {user_to_unfollow.username}."},
                        status=status.HTTP_204_NO_CONTENT)
