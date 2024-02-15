from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.auth.admin import UserAdmin

from fantasy.models import CyberSport, Competition, Team, Player, FantasyTeam, FantasyPlayer, MatchInfoDota, \
    PlayerMatchResult, CompetitionTour
from fantasy.tasks import dota_update, result_from_player_data, get_result, evaluate_match_info
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email']


class CompetitionInlines(admin.StackedInline):
    model = Competition
    extra = 1


class CompetitionTourInlines(admin.StackedInline):
    model = CompetitionTour
    extra = 1


class CyberSportAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    inlines = [CompetitionInlines]


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon', 'editing_start', 'editing_end']
    actions = ('run_dota_update', 'get_players_res', 'get_result', 'evaluate_match_info', )
    inlines = [CompetitionTourInlines]

    @admin.action(description='DOTA UPDATE')
    def run_dota_update(self, request, queryset):
        dota_update()

    @admin.action(description='PLAYERS RESULT')
    def get_players_res(self, request, queryset):
        player_data = {
            'kills': 4,
            'death': 2
        }
        result = result_from_player_data(player_data)
        print("Result:", result)
        result_from_player_data(player_data)

    @admin.action(description='GET RESULT')
    def get_result(self, request, queryset):
        match_info = MatchInfoDota.objects.get(id=120)
        get_result(match_info)

    @admin.action(description='EVALUATE MATCH')
    def evaluate_match_info(self, request, queryset):
        evaluate_match_info()


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
    list_display = ['user', 'player', 'fantasy_team']


class MatchInfoDotaAdmin(admin.ModelAdmin):
    list_display = ['dota_id', 'is_rated']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


class PlayerMatchResultAdmin(admin.ModelAdmin):
    list_display = ['player', 'match_info', 'result']


class CompetitionTourAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'competition']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CyberSport, CyberSportAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(FantasyTeam, FantasyTeamAdmin)
admin.site.register(FantasyPlayer, FantasyPlayerAdmin)
admin.site.register(MatchInfoDota, MatchInfoDotaAdmin)
admin.site.register(PlayerMatchResult, PlayerMatchResultAdmin)
admin.site.register(CompetitionTour, CompetitionTourAdmin)

