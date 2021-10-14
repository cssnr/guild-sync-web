from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'discriminator', 'discord_id', 'is_staff',)
    list_filter = ('is_staff',)
    fieldsets = UserAdmin.fieldsets + (
        ('OAuth', {'fields': ('discord_username', 'discriminator', 'discord_id', 'discord_roles',
                              'blue_team_member', 'blue_team_officer',)}),
    )
    readonly_fields = ('discord_username', 'discriminator', 'discord_id', 'discord_roles',)
    search_fields = ('username', 'discord_id',)
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
