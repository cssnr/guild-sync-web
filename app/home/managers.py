from django.db import models


class ServerProfileManager(models.Manager):
    def get_enabled(self):
        return self.filter(is_enabled=True)
