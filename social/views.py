from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from social.models import Post, Likes
from social.serializers import PostListSerializer, PostDetailSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

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