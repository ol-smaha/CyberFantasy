from django.contrib import admin
from fantasy.models import FantasyTeam, FantasyPlayer, FantasySquadByTour


class FantasySquadByTourInline(admin.StackedInline):
    model = FantasySquadByTour
    extra = 1


class FantasyPlayerInline(admin.StackedInline):
    model = FantasyPlayer
    extra = 1


class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ['user', 'competition', 'result']
    # readonly_fields = ['results_by_tour_string']
    list_filter = ['competition', 'user']
    inlines = [FantasySquadByTourInline]


class FantasySquadByTourAdmin(admin.ModelAdmin):
    list_display = ['fantasy_team', 'competition_tour', 'result']
    list_filter = ['competition_tour']
    search_fields = ['fantasy_team__user__email']
    inlines = [FantasyPlayerInline]


class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = ['player', 'fantasy_team_tour', 'result']


admin.site.register(FantasyTeam, FantasyTeamAdmin)
admin.site.register(FantasySquadByTour, FantasySquadByTourAdmin)
admin.site.register(FantasyPlayer, FantasyPlayerAdmin)
