import threading

from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.auth.admin import UserAdmin

from fantasy.models import Competition, Team, Player, FantasyTeam, FantasyPlayer, Match, \
    PlayerMatchResult, CompetitionTour, FantasyTeamTour, MatchSeries, IgnoreMatch
from fantasy.tasks import competitions_parse_match_ids, parse_matches_data, rate_matches, save_results_to_player, \
    update_fantasy_results
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email']


class CompetitionInline(admin.StackedInline):
    model = Competition
    extra = 0


class CompetitionTourInline(admin.StackedInline):
    model = CompetitionTour
    extra = 0


class FantasyTeamTourInline(admin.StackedInline):
    model = FantasyTeamTour
    extra = 1


class FantasyPlayerInline(admin.StackedInline):
    model = FantasyPlayer
    extra = 1


class PlayerInline(admin.StackedInline):
    model = Player
    extra = 1


class PlayerMatchResultInline(admin.StackedInline):
    model = PlayerMatchResult
    extra = 0
    raw_id_fields = ('match',)


class MatchInline(admin.TabularInline):
    model = Match
    extra = 0
    fields = ['dota_id', 'team_radiant', 'team_dire']
    readonly_fields = ['dota_id', 'team_radiant', 'team_dire']
    show_change_link = True


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_start', 'date_finish', 'status']
    actions = ('parse_matches_ids', )
    inlines = [CompetitionTourInline]

    @admin.action(description='1. Parse Match IDs')
    def parse_matches_ids(self, request, queryset):
        dota_ids = queryset.values_list('dota_id', flat=True)
        t = threading.Thread(target=competitions_parse_match_ids, args=(dota_ids, ))
        t.daemon = True
        t.start()


class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']
    search_fields = ['name', 'short_name']
    inlines = [PlayerInline]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'team', 'game_role', 'cost']
    list_filter = ['game_role', 'cost']
    search_fields = ['nickname']
    inlines = [PlayerMatchResultInline]


class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'result']
    # readonly_fields = ['results_by_tour_string']
    list_filter = ['competition', 'user']
    inlines = [FantasyTeamTourInline]


class FantasyTeamTourAdmin(admin.ModelAdmin):
    list_display = ['fantasy_team', 'competition_tour', 'result']
    list_filter = ['fantasy_team', 'competition_tour']
    inlines = [FantasyPlayerInline]


class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = ['player', 'fantasy_team_tour', 'result']


class MatchSeriesAdmin(admin.ModelAdmin):
    list_display = ['dota_id', 'competition', 'competition_tour']
    search_fields = ['dota_id']
    inlines = [MatchInline]


class MatchAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'dota_id', 'series', 'datetime',
                    'is_filled', 'is_parsed', 'is_rated', 'is_saved_to_players']
    list_filter = ['is_filled', 'is_parsed', 'is_rated', 'is_saved_to_players', 'competition', 'competition_tour']
    search_fields = ['dota_id', 'series__dota_id', 'team_radiant__dota_id', 'team_radiant__dota_id',
                     'team_radiant__name', 'team_dire__name']

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    actions = ('parse_matches_data', 'rate_matches_data', 'save_result_to_players', 'parse_matches_short_data')

    @admin.action(description='2. Parse Full Match Data')
    def parse_matches_data(self, request, queryset):
        dota_ids = queryset.values_list('dota_id', flat=True)
        t = threading.Thread(target=parse_matches_data, args=(dota_ids, ))
        t.daemon = True
        t.start()

    @admin.action(description='2. *** Parse Short Match Data')
    def parse_matches_short_data(self, request, queryset):
        dota_ids = queryset.values_list('dota_id', flat=True)
        t = threading.Thread(target=parse_matches_data, args=(dota_ids, False))
        t.daemon = True
        t.start()

    @admin.action(description='3. Rate Match Data')
    def rate_matches_data(self, request, queryset):
        dota_ids = queryset.values_list('dota_id', flat=True)
        t = threading.Thread(target=rate_matches, args=(dota_ids, ))
        t.daemon = True
        t.start()

    @admin.action(description='4. Save Result To Players')
    def save_result_to_players(self, request, queryset):
        dota_ids = queryset.values_list('dota_id', flat=True)
        t = threading.Thread(target=save_results_to_player, args=(dota_ids, ))
        t.daemon = True
        t.start()


class PlayerMatchResultAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'result']
    search_fields = ['player__nickname', 'match__dota_id']
    raw_id_fields = ('player', 'match',)


class CompetitionTourAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'competition']
    actions = ('update_fantasy_results',)

    @admin.action(description='5. Update Fantasy Results')
    def update_fantasy_results(self, request, queryset):
        ids = queryset.values_list('id', flat=True)
        t = threading.Thread(target=update_fantasy_results, args=(ids,))
        t.daemon = True
        t.start()


class IgnoreMatchAdmin(admin.ModelAdmin):
    list_display = ['dota_id']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(FantasyTeam, FantasyTeamAdmin)
admin.site.register(FantasyTeamTour, FantasyTeamTourAdmin)
admin.site.register(FantasyPlayer, FantasyPlayerAdmin)
admin.site.register(MatchSeries, MatchSeriesAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(PlayerMatchResult, PlayerMatchResultAdmin)
admin.site.register(CompetitionTour, CompetitionTourAdmin)
admin.site.register(IgnoreMatch, IgnoreMatchAdmin)

