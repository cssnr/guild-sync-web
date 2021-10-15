from django.db import models
from .managers import BlueServerManager


class ServerProfile(models.Model):
    server_id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord Server ID')
    server_name = models.CharField(blank=True, max_length=32, verbose_name='Discord Server Name')
    guild_name = models.CharField(blank=True, max_length=64, verbose_name='WoW Guild Name')
    alert_channel = models.CharField(blank=True, max_length=64, verbose_name='Discord Alerts Channel')
    server_notes = models.TextField(blank=True, verbose_name='Server Notes')
    is_enabled = models.BooleanField(default=False, verbose_name='Server Enable Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BlueServerManager()

    def __str__(self):
        return '{} - {}'.format(self.main_char, self.main_class)

    class Meta:
        verbose_name = 'Blue Profile'
        verbose_name_plural = 'Blue Profiles'
