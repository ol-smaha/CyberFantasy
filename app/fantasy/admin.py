from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from fantasy.models import CyberSport, Competition, Team, Player, FantasyTeam, FantasyPlayer
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email']


class CompetitionInlines(admin.StackedInline):
    model = Competition
    extra = 1


class CyberSportAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    inlines = [CompetitionInlines]


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon', 'editing_start', 'editing_end']


class PlayerInlines(admin.StackedInline):
    model = Player
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'cyber_sport', 'icon']
    inlines = [PlayerInlines]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'team', 'game_role', 'icon', 'cost']


class FantasyPlayerInline(admin.StackedInline):
    model = FantasyPlayer
    extra = 1


class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ['name_extended', 'user', 'competition', 'result']
    inlines = [FantasyPlayerInline]


class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'player', 'fantasy_team', 'result']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CyberSport, CyberSportAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(FantasyTeam, FantasyTeamAdmin)
admin.site.register(FantasyPlayer, FantasyPlayerAdmin)
