from django.shortcuts import render
from rest_framework import viewsets

from social.models import Post
from social.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

