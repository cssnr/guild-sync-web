from django.contrib import admin
from .models import BlueProfile


@admin.register(BlueProfile)
class BlueProfileAdmin(admin.ModelAdmin):
    list_display = ('main_char', 'main_class', 'main_role', 'show_in_roster', 'discord_id',)
    list_filter = ('main_class', 'main_role', 'show_in_roster',)
    search_fields = ('title', 'discord_id',)
    ordering = ('main_char',)

    def has_add_permission(self, request, obj=None):
        return False
