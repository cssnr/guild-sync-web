from django.db import models
from .managers import UserProfileManager, ServerProfileManager


class UserProfile(models.Model):
    discord_id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord User ID')
    main_char = models.CharField(unique=True, max_length=32, verbose_name='Main Character')
    main_class = models.CharField(max_length=32, verbose_name='Main Class')
    main_role = models.CharField(max_length=32, verbose_name='Main Role')
    user_description = models.TextField(blank=True, verbose_name='User Description')
    show_in_roster = models.BooleanField(default=True, verbose_name='Show in Roster')
    twitch_username = models.CharField(blank=True, max_length=32, verbose_name='Twitch Username')
    live_on_twitch = models.BooleanField(default=False, verbose_name='Twitch Live Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserProfileManager()

    def __str__(self):
        return 'Discord ID: {}'.format(self.discord_id)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class ServerProfile(models.Model):
    server_id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord Server ID')
    server_name = models.CharField(blank=True, max_length=32, verbose_name='Discord Server Name')
    guild_name = models.CharField(blank=True, max_length=64, verbose_name='WoW Guild Name')
    alert_channel = models.CharField(blank=True, max_length=64, verbose_name='Discord Alerts Channel')
    server_notes = models.TextField(blank=True, verbose_name='Server Notes')
    is_enabled = models.BooleanField(default=False, verbose_name='Server Enable Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ServerProfileManager()

    def __str__(self):
        return '{} ({})'.format(self.server_name, self.server_id)

    class Meta:
        verbose_name = 'Server Profile'
        verbose_name_plural = 'Server Profiles'
