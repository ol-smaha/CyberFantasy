from django.contrib import admin

from fantasy.models import CyberSport, Competition, User, Team, Player, FantasyTeam, FantasyPlayer


class CompetitionInlines(admin.StackedInline):
    model = Competition
    extra = 1


class CyberSportAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    inlines = [CompetitionInlines]


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon']


class UserAdmin(admin.ModelAdmin):
    list_display = ['nickname']


class PlayerInlines(admin.StackedInline):
    model = Player
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'cyber_sport', 'icon']
    inlines = [PlayerInlines]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'team', 'game_role', 'icon']


class FantasyPlayerInline(admin.StackedInline):
    model = FantasyPlayer
    extra = 1


class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'result', 'name_extended']
    inlines = [FantasyPlayerInline]


class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'player', 'fantasy_team', 'result', 'quantity']


admin.site.register(CyberSport, CyberSportAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(FantasyTeam, FantasyTeamAdmin)
admin.site.register(FantasyPlayer, FantasyPlayerAdmin)
