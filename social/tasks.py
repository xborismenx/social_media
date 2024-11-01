# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Post

@shared_task
def publish_scheduled_posts():
    now = timezone.now()
    scheduled_posts = Post.objects.filter(scheduled_time__lte=now, date_posted__isnull=True)

    for post in scheduled_posts:
        post.date_posted = now
        post.save()
