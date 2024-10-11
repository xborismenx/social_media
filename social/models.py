from django.contrib.auth import get_user_model
from django.db import models

from user.models import User


class Post(models.Model):
    text = models.TextField(max_length=500)
    image = models.ImageField(upload_to='posts/')
    owner = models.ForeignKey(get_user_model(), models.CASCADE, related_name="owner_post")


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    liked_at = models.DateTimeField(auto_now_add=True)


