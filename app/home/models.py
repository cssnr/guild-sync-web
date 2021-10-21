from django.db import models
from .managers import ServerProfileManager


class ServerProfile(models.Model):
    server_id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord Server ID')
    server_name = models.CharField(blank=True, max_length=32, verbose_name='Discord Server Name')
    guild_name = models.CharField(blank=True, max_length=64, verbose_name='WoW Guild Name')
    guild_realm = models.CharField(blank=True, max_length=32, verbose_name='WoW Guild Realm')
    guild_role = models.CharField(blank=True, max_length=32, verbose_name='Discord Guild Role')
    alert_channel = models.CharField(blank=True, max_length=32, verbose_name='Discord Alerts Channel')
    server_notes = models.TextField(blank=True, verbose_name='Server Notes')
    sync_method = models.CharField(default=False, max_length=32, verbose_name='Sync Method')
    sync_classes = models.BooleanField(default=False, verbose_name='Sync Class Roles')
    is_enabled = models.BooleanField(default=False, verbose_name='Server Enable Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ServerProfileManager()

    def __str__(self):
        return f'{self.server_id} - {self.server_name}'

    class Meta:
        verbose_name = 'Server Profile'
        verbose_name_plural = 'Server Profiles'
