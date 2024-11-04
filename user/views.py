from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from user.models import Follow, User
from user.serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer, UserFollower, UserFollowing


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserListSerializer

    def get_queryset(self):
        queryset = self.queryset

        queryset = queryset.annotate(
            followers_count=Count('followers'),
            following_count=Count('following')
        )

        username = self.request.query_params.get('username')
        first_name = self.request.query_params.get('first_name')
        last_name = self.request.query_params.get('last_name')
        email = self.request.query_params.get('email')
        country = self.request.query_params.get('country')

        if username:
            queryset = queryset.filter(username__icontains=username)

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_authentication_classes(self):
        if self.action == 'create':
            return []
        return [JWTAuthentication]

    @action(detail=False, methods=['GET', "POST"], permission_classes=[IsAuthenticated()])
    def me(self, request):
        """returns the data of the current authenticated user"""
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated()])
    def followers(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserFollower(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated()])
    def following(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserFollowing(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated()])
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

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated()])
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
