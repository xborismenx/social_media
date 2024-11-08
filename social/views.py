from datetime import datetime

from django.db.models import Prefetch, OuterRef, Exists
from django.utils import timezone
from django.utils.timezone import make_aware
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from social.models import Post, Likes, Comments
from social.serializers import PostListSerializer, PostDetailSerializer, CommentsCreateSerializer
from user.models import Follow


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action in ["create", "retrieve", "update", "partial_update"]:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if user.is_authenticated:
            likes_subquery = Likes.objects.filter(
                post=OuterRef("pk"),
                user=user
            )
            queryset = Post.objects.select_related("owner").prefetch_related(
                Prefetch("images"),
                Prefetch("tags"),
                Prefetch("post_likes"),
                Prefetch("post_comments"),
            ).annotate(
                is_liked=Exists(likes_subquery)
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("post_comments__user")

        text = self.request.query_params.get('text')
        tags = self.request.query_params.get('tags')
        date_lt = self.request.query_params.get('date_lt')
        date_gt = self.request.query_params.get('date_gt')
        owner = self.request.query_params.get('owner')

        queryset = queryset.filter(date_posted__lte=timezone.now())

        if text:
            queryset = queryset.filter(text__icontains=text)

        if tags:
            tags_list = [int(tag) for tag in tags.split(',')]
            queryset = queryset.filter(tags__tag_post__id__in=tags_list)

        if date_lt:
            date = make_aware(datetime.strptime(date_lt, '%d.%m.%Y'))
            queryset = queryset.filter(date_posted__lte=date)

        if date_gt:
            date = make_aware(datetime.strptime(date_gt, '%d.%m.%Y'))
            queryset = queryset.filter(date_posted__gte=date)

        if owner:
            queryset = queryset.filter(owner=owner)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "text",
                type=OpenApiTypes.STR,
                description="Text filter: searches for occurrences of the provided text in the `text` field (e.g., ?text=example)."
            ),
            OpenApiParameter(
                "tags",
                type=OpenApiTypes.STR,
                description="Tags filter: accepts a comma-separated list of tag IDs (e.g., ?tags=1,2,3)."
            ),
            OpenApiParameter(
                "date_lt",
                type=OpenApiTypes.DATE,
                description="Date filter (less than or equal): accepts a date in the format `YYYY-MM-DD` (e.g., ?date_lt=2023-01-01)."
            ),
            OpenApiParameter(
                "date_gt",
                type=OpenApiTypes.DATE,
                description="Date filter (greater than or equal): accepts a date in the format `YYYY-MM-DD` (e.g., ?date_gt=2023-01-01)."
            ),
            OpenApiParameter(
                "owner",
                type=OpenApiTypes.INT,
                description="Owner filter: accepts a user ID to filter by the owner (e.g., ?owner=1)."
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @extend_schema(
        description="Like a post. If the post is already liked by the user, returns a 400 status.",
        request=None,
        responses={
            201: {"status": "post liked"},
            400: {"status": "post already liked"}
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated()])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if not Likes.objects.filter(user=user, post=post).exists():
            Likes.objects.create(user=user, post=post)
            return Response({"status": "post liked"}, status=status.HTTP_201_CREATED)
        return Response({"status": "post already liked"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Dislike a post. If the post is already liked by the user, returns a 400 status.",
        request=None,
        responses={
            204: None,
            400: {"status": "post not liked"}
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated()])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like = Likes.objects.filter(user=user, post=post)
        if like.exists():
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "post not liked"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="retrieving users posts subscribed by the user",
        responses={
            status.HTTP_200_OK: PostListSerializer,
        }
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated()])
    def subscribed_posts(self, request):
        """retrieving posts subscribed by the user"""
        queryset = self.get_queryset()
        user = request.user
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        posts = queryset.filter(owner__in=following_users)
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        description="retrieving posts created by user",
        responses={
            status.HTTP_200_OK: PostListSerializer,
        }
    )
    @action(detail=False, methods=["get", "post"], permission_classes=[IsAuthenticated()])
    def my_posts(self, request):
        queryset = self.get_queryset()
        user = request.user
        posts = queryset.filter(owner=user)
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        description="retrieving posts what liked by user",
        responses={
            status.HTTP_200_OK: PostDetailSerializer,
        }
    )
    @action(detail=False, methods=["GET"], permission_classes=[IsAuthenticated()])
    def liked_posts(self, request):
        queryset = self.get_queryset()
        user = request.user
        likes = Likes.objects.filter(user=user).values_list('post', flat=True)
        posts = queryset.filter(id__in=likes)
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        request=CommentsCreateSerializer,
        responses={
            status.HTTP_201_CREATED: CommentsCreateSerializer,
            status.HTTP_400_BAD_REQUEST: {'description': 'Comment text is required.'}
        },
    )
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated()])
    def comment(self, request, pk=None):
        user = request.user
        post = self.get_object()
        comment_text = request.data.get("comment")

        if not comment_text:
            return Response({"detail": "Comment text is required."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comments.objects.create(user=user, post=post, comment=comment_text)

        serializer = CommentsCreateSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
