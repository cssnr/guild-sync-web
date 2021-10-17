from django.db import models


class UserProfileManager(models.Manager):
    def get_active(self):
        return self.filter(show_in_roster=True)

    def get_live(self):
        return self.filter(live_on_twitch=True)


class ServerProfileManager(models.Manager):
    def get_enabled(self):
        return self.filter(is_enabled=True)
