from django.db import models
from django.db.models import Sum
from django.utils import timezone


from fantasy.constants import CompetitionStatusEnum, GameRoleEnum
from users.models import CustomUser


class Team(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=8, null=True, blank=True)
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    dota_id = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=128)
    date_start = models.DateField(null=True, blank=True)
    date_finish = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=64, choices=CompetitionStatusEnum.choices())
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    dota_id = models.CharField(max_length=128, default='')
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
        ordering = ['nickname']

    nickname = models.CharField(max_length=128, null=True, blank=True)
    team = models.ForeignKey(to=Team, on_delete=models.SET_NULL,
                             related_name='players', null=True, blank=True)
    game_role = models.CharField(max_length=64, choices=GameRoleEnum.choices())
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    cost = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    dota_id = models.CharField(max_length=128, default='')

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
        return self.name_extended


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
        print(res)
        self.result = res or 0
        self.save()


class FantasyPlayer(models.Model):
    player = models.ForeignKey(to=Player, on_delete=models.SET_NULL,
                               null=True, blank=True)
    fantasy_team_tour = models.ForeignKey(to=FantasyTeamTour, on_delete=models.SET_NULL,
                                          related_name='fantasy_players', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def set_result(self):
        res = PlayerMatchResult.objects.filter(
            player=self.player,
            match__in=self.fantasy_team_tour.competition_tour.matches.all(),
        ).aggregate(total_result=Sum('result'))['total_result']
        self.result = res or 0
        self.save()


class Match(models.Model):
    dota_id = models.CharField(max_length=128, default='')
    data = models.JSONField(null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    competition = models.ForeignKey(to=Competition, on_delete=models.CASCADE,
                                    related_name='matches', null=True, blank=True)
    competition_tour = models.ForeignKey(to=CompetitionTour, on_delete=models.SET_NULL,
                                         related_name='matches', null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    is_parsed = models.BooleanField(default=False)
    is_rated = models.BooleanField(default=False)
    is_saved_to_players = models.BooleanField(default=False)

    def __str__(self):
        return self.dota_id


class PlayerMatchResult(models.Model):
    player = models.ForeignKey(to=Player, on_delete=models.SET_NULL,
                               related_name='players_res', null=True, blank=True)
    match = models.ForeignKey(to=Match, on_delete=models.SET_NULL,
                              related_name='players_res', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)






