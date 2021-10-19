from django.db import models


class ServerProfileManager(models.Manager):
    def get_enabled(self):
        return self.filter(is_enabled=True)

    def get_by_guild(self, guild, realm):
        return super().get_queryset().filter(
            guild_name__icontains=guild).filter(
            guild_realm__icontains=realm).first()
