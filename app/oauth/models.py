from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    discord_username = models.CharField(blank=True, max_length=32)
    discriminator = models.CharField(blank=True, max_length=4)
    discord_id = models.CharField(blank=True, max_length=32)
    avatar_hash = models.CharField(blank=True, max_length=32)

    def __str__(self):
        return self.username
