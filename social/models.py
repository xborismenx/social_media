from django.contrib.auth import get_user_model
from django.db import models

from user.models import User


class PostImage(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='posts/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Tags(models.Model):
    tag_name = models.CharField(max_length=50, unique=True)


class Post(models.Model):
    text = models.TextField(max_length=500)
    owner = models.ForeignKey(get_user_model(), models.CASCADE, related_name="owner_post")
    date_posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tags, related_name="tag_post")


class Likes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    liked_at = models.DateTimeField(auto_now_add=True)
