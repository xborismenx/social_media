from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from social.models import Post, Likes
from social.serializers import PostListSerializer, PostDetailSerializer
from user.models import Follow


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def get_queryset(self):
        text = self.request.query_params.get('text')
        tags = self.request.query_params.get('tags')
        date_lt = self.request.query_params.get('date_lt')
        date_gt = self.request.query_params.get('date_gt')
        owner = self.request.query_params.get('owner')

        queryset  = self.queryset

        if text:
            queryset = queryset.filter(text__icontains=text)

        if tags:
            tags_list = [int(tag) for tag in tags.split(',')]
            queryset = queryset.filter(tags__tag_post__id__in=tags_list)

        if date_lt:
            date = datetime.strptime(date_lt, '%d.%m.%Y')
            queryset = queryset.filter(date_posted__lte=date)


        if date_gt:
            date = datetime.strptime(date_gt, '%d.%m.%Y')
            queryset = queryset.filter(date_posted__gte=date)

        if owner:
            queryset = queryset.filter(owner=owner)

        return queryset



    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if not Likes.objects.filter(user=user, post=post).exists():
            Likes.objects.create(user=user, post=post)
            return Response({"status": "post liked"}, status=status.HTTP_201_CREATED)
        return Response({"status": "post already liked"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like = Likes.objects.filter(user=user, post=post)
        if like.exists():
            like.delete()
            return Response({"status": "post unliked"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"status": "post not liked"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=["get"])
    def subscribed_posts(self, request):
        """retrieving posts subscribed by the user"""
        user = request.user
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        print(following_users)

        posts = Post.objects.filter(owner__in=following_users)
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"])
    def my_posts(self, request):
        user = request.user
        posts = Post.objects.filter(owner=user)
        serializer = PostListSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)
