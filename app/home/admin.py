from django.contrib import admin
from .models import UserProfile, ServerProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('main_char', 'main_class', 'main_role', 'show_in_roster', 'discord_id',)
    list_filter = ('main_class', 'main_role', 'show_in_roster',)
    search_fields = ('title', 'discord_id',)
    ordering = ('main_char',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ServerProfile)
class ServerProfileAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'server_name', 'guild_name', 'alert_channel', 'is_enabled',)
    list_filter = ('is_enabled',)
    search_fields = ('server_id', 'server_name', 'guild_name',)
    ordering = ('server_name',)

    def has_add_permission(self, request, obj=None):
        return False
