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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Username filter: searches for occurrences of the provided username (e.g., ?username=johndoe)."
            ),
            OpenApiParameter(
                "first_name",
                type=OpenApiTypes.STR,
                description="First name filter: searches for occurrences of the provided first name (e.g., ?first_name=John)."
            ),
            OpenApiParameter(
                "last_name",
                type=OpenApiTypes.STR,
                description="Last name filter: searches for occurrences of the provided last name (e.g., ?last_name=Doe)."
            ),
            OpenApiParameter(
                "email",
                type=OpenApiTypes.STR,
                description="Email filter: searches for occurrences of the provided email address (e.g., ?email=john@example.com)."
            ),
            OpenApiParameter(
                "country",
                type=OpenApiTypes.STR,
                description="Country filter: searches for occurrences of the provided country name (e.g., ?country=USA)."
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
        followers_prefetch = Prefetch('followers',
                                      queryset=Follow.objects.filter(following=user).select_related('follower'))
        following_prefetch = Prefetch('following',
                                      queryset=Follow.objects.filter(follower=user).select_related('following'))

        queryset = self.queryset.filter(pk=user.pk).prefetch_related(followers_prefetch, following_prefetch)
        serializer = UserDetailSerializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated()])
    def followers(self, request, pk=None):
        """return the data of the followers of the current authenticated user"""
        followers_prefetch = Prefetch('followers',
                                      queryset=Follow.objects.filter(following__pk=pk).select_related('follower'))
        queryset = self.queryset.filter(pk=pk).prefetch_related(followers_prefetch)
        user = queryset.first()
        if user:
            serializer = UserFollower(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated()])
    def following(self, request, pk=None):
        """return the data of the followings of the current authenticated user"""
        following_prefetch = Prefetch('following',
                                      queryset=Follow.objects.filter(follower__pk=pk).select_related('following'))
        queryset = self.queryset.filter(pk=pk).prefetch_related(following_prefetch)
        user = queryset.first()
        if user:
            serializer = UserFollowing(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated()])
    def follow(self, request, pk=None):
        """follow user by their id"""
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
        """unfollow user by their id"""
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
