from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'ADMIN'),
        (MODERATOR, 'MODERATOR'),
        (USER, 'USER')
    ]
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=USER)
