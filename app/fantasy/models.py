from django.db import models

from fantasy.constants import CompetitionStatusEnum, GameRoleEnum
from users.models import CustomUser


class CyberSport(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    cyber_sport = models.ForeignKey(to=CyberSport, on_delete=models.SET_NULL,
                                    related_name='teams', null=True, blank=True)
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    dota_id = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=128)
    date_start = models.DateField(null=True, blank=True)
    date_finish = models.DateField(null=True, blank=True)
    cyber_sport = models.ForeignKey(to=CyberSport, on_delete=models.SET_NULL,
                                    related_name='competitions', null=True, blank=True)
    status = models.CharField(max_length=64, choices=CompetitionStatusEnum.choices())
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    dota_id = models.CharField(max_length=128, default='')
    team = models.ManyToManyField(to=Team, related_name='competitions')

    def __str__(self):
        return self.name


class Player(models.Model):
    nickname = models.CharField(max_length=128, null=True, blank=True)
    team = models.ForeignKey(to=Team, on_delete=models.SET_NULL,
                             related_name='players', null=True, blank=True)
    game_role = models.CharField(max_length=64, choices=GameRoleEnum.choices())
    icon = models.ImageField(upload_to='media/', null=True, blank=True)
    cost = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        return self.nickname


class FantasyTeam(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE,
                             related_name='fantasy_teams', null=True, blank=True)
    competition = models.ForeignKey(to=Competition,  on_delete=models.CASCADE,
                                    related_name='fantasy_teams', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name_extended = models.CharField(max_length=128, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'competition'], name='competition and user unique'),
        ]

    def __str__(self):
        return self.name_extended


class FantasyPlayer(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE,
                             related_name='fantasy_users', null=True, blank=True)
    player = models.ForeignKey(to=Player, on_delete=models.SET_NULL,
                               null=True, blank=True)
    fantasy_team = models.ForeignKey(to=FantasyTeam, on_delete=models.SET_NULL,
                                     related_name='fantasy_players', null=True, blank=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, default=0)











