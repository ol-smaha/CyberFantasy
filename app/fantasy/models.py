from django.db import models
from django.db.models import Sum
from django.utils import timezone


from fantasy.constants import CompetitionStatusEnum, GameRoleEnum, MatchSeriesBOFormatEnum
from users.models import CustomUser


class Team(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=8, null=True, blank=True)
    dota_id = models.CharField(max_length=128, default='', unique=True)

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=128)
    date_start = models.DateField(null=True, blank=True)
    date_finish = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=64, choices=CompetitionStatusEnum.choices())
    dota_id = models.CharField(max_length=128, default='', unique=True)
    team = models.ManyToManyField(to=Team, related_name='competitions')
    active_tour = models.OneToOneField(to='CompetitionTour', related_name='parent_competition',
                                       on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_editing_allowed(self):
        return self.active_tour.is_editing_allowed if self.active_tour else False

    def __str__(self):
        return self.name


class CompetitionTour(models.Model):
    STATUSES = (
        ('expected', 'expected'),
        ('ongoing', 'ongoing'),
        ('finished', 'finished'),
    )
    name = models.CharField(max_length=32, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE,
                                    related_name='competition_tours', null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUSES, default='expected')
    editing_start = models.DateTimeField(null=True, blank=True)
    editing_end = models.DateTimeField(null=True, blank=True)

    @property
    def is_editing_allowed(self):
        if self.editing_start and self.editing_end:
            current_date = timezone.now()
            return self.editing_start <= current_date <= self.editing_end
        else:
            return False

    def __str__(self):
        return self.name or f'Tour: {self.pk}'


class Player(models.Model):
    class Meta:
        ordering = ['-cost', 'team__name', 'nickname']

    nickname = models.CharField(max_length=128, null=True, blank=True)
    team = models.ForeignKey(to=Team, on_delete=models.SET_NULL,
                             related_name='players', null=True, blank=True)
    game_role = models.CharField(max_length=64, choices=GameRoleEnum.choices())
    cost = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    dota_id = models.CharField(max_length=128, default='', unique=True)

    def __str__(self):
        return self.nickname


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


class FantasyTeamTour(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['fantasy_team', 'competition_tour'],
                                    name='fantasy_team and competition_tour unique'),
        ]
    fantasy_team = models.ForeignKey(to=FantasyTeam, on_delete=models.CASCADE, related_name='child_teams')
    competition_tour = models.ForeignKey(to=CompetitionTour,  on_delete=models.CASCADE,
                                         related_name='fantasy_teams', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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
    fantasy_team_tour = models.ForeignKey(to=FantasyTeamTour, on_delete=models.SET_NULL,
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


class MatchSeries(models.Model):
    dota_id = models.CharField(max_length=128, default='', unique=True)
    bo_format = models.CharField(max_length=8, choices=MatchSeriesBOFormatEnum.choices(), blank=True, null=True)
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE,
                                    related_name='match_series', null=True, blank=True)
    competition_tour = models.ForeignKey(to=CompetitionTour, on_delete=models.SET_NULL,
                                         related_name='match_series', null=True, blank=True)

    def __str__(self):
        return f'{self.dota_id} - {self.bo_format}'


class Match(models.Model):
    dota_id = models.CharField(max_length=128, default='', unique=True)
    series = models.ForeignKey(to=MatchSeries, related_name='matches',
                               blank=True, null=True, on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE,
                                    related_name='matches', null=True, blank=True)
    competition_tour = models.ForeignKey(to=CompetitionTour, on_delete=models.SET_NULL,
                                         related_name='matches', null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    team_radiant = models.ForeignKey(to=Team, related_name='matches_radiant',
                                     blank=True, null=True, on_delete=models.SET_NULL)
    team_dire = models.ForeignKey(to=Team, related_name='matches_dire',
                                  blank=True, null=True, on_delete=models.SET_NULL)
    is_parsed = models.BooleanField(default=False)
    is_filled = models.BooleanField(default=False)
    is_rated = models.BooleanField(default=False)
    is_saved_to_players = models.BooleanField(default=False)

    def get_competition_name(self):
        if self.competition:
            return self.competition.name
        else:
            return '*Competition'

    def get_competition_tour_name(self):
        if self.competition_tour:
            return self.competition_tour.name
        else:
            return '*Tour'

    def get_team_radiant_name(self):
        if self.team_radiant:
            return self.team_radiant.name
        else:
            return '*Radiant'

    def get_team_dire_name(self):
        if self.team_dire:
            return self.team_dire.name
        else:
            return '*Dire'

    @property
    def full_name(self):
        return (f"{self.get_competition_name()}/{self.get_competition_tour_name()}: "
                f"{self.get_team_radiant_name()} - {self.get_team_dire_name()}")

    def __str__(self):
        return self.full_name


class PlayerMatchResult(models.Model):
    player = models.ForeignKey(to=Player, on_delete=models.CASCADE,
                               related_name='players_res', null=True, blank=True)
    match = models.ForeignKey(to=Match, on_delete=models.CASCADE,
                              related_name='players_res', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.player.nickname} - {self.match}'


class IgnoreMatch(models.Model):
    dota_id = models.CharField(max_length=128, default='', unique=True)

    def __str__(self):
        return self.dota_id


