import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

from user.models import User


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.post.owner)}-{uuid.uuid4()}{extension}"
    return os.path.join('uploads/posts/', filename)


class PostImage(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=post_image_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    text = models.TextField(max_length=500)
    owner = models.ForeignKey(get_user_model(), models.CASCADE, related_name="owner_post")
    date_posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tags, related_name="tag_post")


class Likes(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'post'),)
