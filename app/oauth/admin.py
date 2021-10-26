from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'discriminator', 'is_superuser',)
    list_filter = ('is_superuser',)
    fieldsets = UserAdmin.fieldsets + (
        ('OAuth', {'fields': ('discriminator', 'avatar_hash', 'server_list',)}),
    )
    readonly_fields = ('discriminator', 'avatar_hash', 'server_list',)
    search_fields = ('first_name', 'discriminator',)
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
