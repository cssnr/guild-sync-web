from django.contrib import admin
from .models import ServerProfile


@admin.register(ServerProfile)
class ServerProfileAdmin(admin.ModelAdmin):
    list_display = ('server_name', 'server_id', 'guild_name', 'alert_channel', 'is_enabled',)
    list_filter = ('is_enabled',)
    search_fields = ('server_id', 'server_name', 'guild_name',)
    ordering = ('server_name',)

    def has_add_permission(self, request, obj=None):
        return False
