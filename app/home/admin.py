from django.contrib import admin
from .models import BlueProfile, BlueNews, GuildApplicants


@admin.register(BlueProfile)
class BlueProfileAdmin(admin.ModelAdmin):
    list_display = ('main_char', 'main_class', 'main_role', 'show_in_roster', 'discord_id',)
    list_filter = ('main_class', 'main_role', 'show_in_roster',)
    search_fields = ('title', 'discord_id',)
    ordering = ('main_char',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BlueNews)
class BlueNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_name', 'published', 'created_at')
    list_filter = ('published',)
    search_fields = ('title',)
    ordering = ('-created_at',)


@admin.register(GuildApplicants)
class GuildApplicantsAdmin(admin.ModelAdmin):
    list_display = ('char_name', 'char_role', 'fri_raid', 'sat_raid', 'tue_raid', 'app_status',)
    list_filter = ('app_status', 'fri_raid', 'sat_raid', 'tue_raid', 'char_role',)
    readonly_fields = ('char_name', 'char_role', 'warcraft_logs', 'speed_test', 'spoken_langs', 'native_lang',
                       'fri_raid', 'sat_raid', 'tue_raid', 'raid_exp', 'why_blue', 'contact_info',)
    search_fields = ('char_name',)
    ordering = ('-pk',)

    def has_add_permission(self, request, obj=None):
        return False
