from django.db import models


class BlueProfileManager(models.Manager):
    def get_active(self):
        return self.filter(show_in_roster=True)

    def get_live(self):
        return self.filter(live_on_twitch=True)
