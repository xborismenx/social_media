from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='users/', null=True)
    city = models.CharField(max_length=60, blank=True)
    country = models.CharField(max_length=60, blank=True)
    birth_date = models.DateField(null=True)
    bio = models.TextField(max_length=500, blank=True)

