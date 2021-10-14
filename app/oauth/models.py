from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    discord_username = models.CharField(blank=True, max_length=32)
    discriminator = models.CharField(blank=True, max_length=4)
    discord_id = models.CharField(blank=True, max_length=32)
    avatar_hash = models.CharField(blank=True, max_length=32)
    blue_team_member = models.BooleanField(blank=True, default=False)
    blue_team_officer = models.BooleanField(blank=True, default=False)
    discord_roles = models.JSONField(blank=True, default=list)

    def __str__(self):
        return self.username
