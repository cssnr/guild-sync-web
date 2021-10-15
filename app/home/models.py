from django.db import models
from .managers import BlueProfileManager


class BlueProfile(models.Model):
    discord_id = models.CharField(primary_key=True, max_length=32, verbose_name='Discord ID')
    main_char = models.CharField(unique=True, max_length=32, verbose_name='Main Character')
    main_class = models.CharField(max_length=32, verbose_name='Main Class')
    main_role = models.CharField(max_length=32, verbose_name='Main Role')
    user_description = models.TextField(blank=True, verbose_name='User Description')
    show_in_roster = models.BooleanField(default=True, verbose_name='Show in Roster')
    twitch_username = models.CharField(blank=True, max_length=32, verbose_name='Twitch Username')
    live_on_twitch = models.BooleanField(default=False, verbose_name='Twitch Live Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BlueProfileManager()

    def __str__(self):
        return '{} - {}'.format(self.main_char, self.main_class)

    class Meta:
        verbose_name = 'Blue Profile'
        verbose_name_plural = 'Blue Profiles'


class TwitchToken(models.Model):
    access_token = models.CharField(blank=True, max_length=32)
    expiration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.access_token
