from django.views.generic import DetailView

from fantasy.constants import GameRoleEnum
from fantasy.models import Competition, Player


# Create your views here.
class FantasyTeamView(DetailView):
    model = Competition
    pk_url_kwarg = 'tournament_id'
    template_name = 'team.html'

    def get_fantasy_team_tour(self, *args, **kwargs):
        print('***** 0000000000000')
        tournament = self.get_object()
        tour = tournament.competition_tours.filter(status='ongoing').last()
        fantasy_team = tournament.fantasy_teams.filter(user=self.request.user).last()
        fantasy_team_tour = fantasy_team.child_teams.filter(competition_tour=tour).last()
        return fantasy_team_tour

    def get_all_tournament_players(self, *args, **kwargs):
        players = Player.objects.filter(team__in=self.get_object().team.all().values_list('pk', flat=True))
        return players

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        fantasy_team_tour = self.get_fantasy_team_tour()
        players = self.get_all_tournament_players().exclude(pk__in=fantasy_team_tour.fantasy_players.all().values_list('player__pk', flat=True))

        context_data['fantasy_team_tour'] = fantasy_team_tour
        context_data['current_carry'] = fantasy_team_tour.fantasy_players.filter(player__game_role=GameRoleEnum.CARRY).last()
        context_data['current_mid'] = fantasy_team_tour.fantasy_players.filter(player__game_role=GameRoleEnum.MID).last()
        context_data['current_offlane'] = fantasy_team_tour.fantasy_players.filter(player__game_role=GameRoleEnum.HARD).last()
        context_data['current_semi_support'] = fantasy_team_tour.fantasy_players.filter(player__game_role=GameRoleEnum.SUPPORT_4).last()
        context_data['current_full_support'] = fantasy_team_tour.fantasy_players.filter(player__game_role=GameRoleEnum.SUPPORT_5).last()

        context_data['players_carry'] = players.filter(game_role=GameRoleEnum.CARRY)
        context_data['players_mid'] = players.filter(game_role=GameRoleEnum.MID)
        context_data['players_offlane'] = players.filter(game_role=GameRoleEnum.HARD)
        context_data['players_semi_support'] = players.filter(game_role=GameRoleEnum.SUPPORT_4)
        context_data['players_full_support'] = players.filter(game_role=GameRoleEnum.SUPPORT_5)
        print(context_data)
        return context_data

