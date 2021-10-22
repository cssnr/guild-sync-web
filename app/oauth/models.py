import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models


def random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    discord_username = models.CharField(blank=True, max_length=32)
    discriminator = models.CharField(blank=True, max_length=4)
    discord_id = models.CharField(blank=True, max_length=32)
    avatar_hash = models.CharField(blank=True, max_length=32)
    access_token = models.CharField(blank=True, max_length=32)
    access_key = models.CharField(default=random_string, max_length=32)
    server_list = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.username
