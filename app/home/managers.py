from django.db import models


class BlueServerManager(models.Manager):
    def get_enabled(self):
        return self.filter(is_enabled=True)
