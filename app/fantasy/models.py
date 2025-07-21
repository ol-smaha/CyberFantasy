from django.db import models
from django.db.models import Sum

from fantasy.constants import MatchSeriesBOFormatEnum
from real.models import Competition, CompetitionTour, Player, PlayerMatchResult, MatchSeries
from users.models import CustomUser


class FantasyTeam(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'competition'], name='competition and user unique'),
        ]

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE,
                             related_name='fantasy_teams', null=True, blank=True)
    competition = models.ForeignKey(to=Competition,  on_delete=models.CASCADE,
                                    related_name='fantasy_teams', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name_extended = models.CharField(max_length=128, unique=True)

    @property
    def edit(self):
        return True if self.competition.is_editing_allowed else False

    def set_result(self):
        res = self.child_teams.all().aggregate(total_result=Sum('result'))['total_result']
        self.result = res or 0
        self.save()

    @property
    def results_by_tour(self):
        qs = (self.child_teams.all()
                  .values('competition_tour')
                  .annotate(res=Sum('result'))
                  .order_by('competition_tour'))
        return qs

    @property
    def results_by_tour_string(self):
        results = ""
        for tour in self.results_by_tour:
            results += f"{tour['competition_tour']}: {float(tour['res'])}\n"
        return results

    def __str__(self):
        return f'{self.user}: {self.competition.name}'


class FantasySquadByTour(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fantasy_team', 'competition_tour'],
                                    name='fantasy_team and competition_tour unique'),
        ]
    fantasy_team = models.ForeignKey(to=FantasyTeam, on_delete=models.CASCADE, related_name='child_teams')
    competition_tour = models.ForeignKey(to=CompetitionTour,  on_delete=models.CASCADE,
                                         related_name='fantasy_teams', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    player_carry = models.ForeignKey(to='FantasyPlayer',  on_delete=models.SET_NULL,
                                     related_name='fantasy_tours_when_pick_this_carry', null=True, blank=True)
    player_mid = models.ForeignKey(to='FantasyPlayer',  on_delete=models.SET_NULL,
                                   related_name='fantasy_tours_when_pick_this_mid', null=True, blank=True)
    player_offlane = models.ForeignKey(to='FantasyPlayer',  on_delete=models.SET_NULL,
                                       related_name='fantasy_tours_when_pick_this_offlane', null=True, blank=True)
    player_semi_support = models.ForeignKey(to='FantasyPlayer',  on_delete=models.SET_NULL,
                                            related_name='fantasy_tours_when_pick_this_semi_support', null=True, blank=True)
    player_full_support = models.ForeignKey(to='FantasyPlayer',  on_delete=models.SET_NULL,
                                             related_name='fantasy_tours_when_pick_this_full_support', null=True, blank=True)

    def set_result(self):
        res = self.fantasy_players.all().aggregate(total_result=Sum('result'))['total_result']
        self.result = res or 0
        self.save()

    def get_competition_tour_name(self):
        if self.competition_tour:
            return self.competition_tour.name
        else:
            return '*Tour'

    def __str__(self):
        return f'{self.fantasy_team.user}|{self.competition_tour.name}'


class FantasyPlayer(models.Model):
    player = models.ForeignKey(to=Player, on_delete=models.SET_NULL,
                               null=True, blank=True)
    fantasy_team_tour = models.ForeignKey(to=FantasySquadByTour, on_delete=models.SET_NULL,
                                          related_name='fantasy_players', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def set_result(self):
        series_ids = self.player.players_res.filter(
            match__competition_tour=self.fantasy_team_tour.competition_tour
        ).values_list('match__series', flat=True).distinct()
        series_qs = MatchSeries.objects.filter(id__in=series_ids)
        total_result = 0

        for series in series_qs:
            matches = series.matches.all()
            match_count = matches.count()
            if series.bo_format == MatchSeriesBOFormatEnum.BO3 and match_count == 3:
                series_tot_res = (PlayerMatchResult.objects.filter(
                    match__in=matches,
                    player=self.player
                ).aggregate(series_sum_res=Sum('result')))['series_sum_res']
                series_avg_res = series_tot_res / 3 * 2
                total_result += series_avg_res
            elif series.bo_format == MatchSeriesBOFormatEnum.BO5 and match_count <= 3:
                series_tot_res = (PlayerMatchResult.objects.filter(
                    match__in=matches,
                    player=self.player
                ).aggregate(series_sum_res=Sum('result')))['series_sum_res']
                series_avg_res = series_tot_res / match_count * 3
                total_result += series_avg_res
            else:
                series_tot_res = PlayerMatchResult.objects.filter(
                    player=self.player,
                    match__in=matches,
                ).aggregate(finally_res=Sum('result'))['finally_res']
                total_result += series_tot_res

        self.result = total_result or 0
        self.save()

    def __str__(self):
        return f'{self.player.nickname} - {self.fantasy_team_tour}'
