import random
import time
from datetime import datetime

from django.conf import settings

from celery import shared_task
from api.connectors import DotaApiConnector
from core.celery_app import app
from fantasy.constants import CompetitionStatusEnum, GameRoleEnum, MatchSeriesBOFormatEnum
from fantasy.models import (Competition, Match, Player, PlayerMatchResult, CompetitionTour, MatchSeries, Team,
                            IgnoreMatch)

api_connector = DotaApiConnector()


@shared_task(name='1. Збір та групування матчів.')
def competitions_parse_match_ids_celery_task():
    print('--- START competitions_parse_match_ids_task')
    obj_ids = Competition.objects.filter(status=CompetitionStatusEnum.STARTED).values_list('dota_id', flat=True)
    print(f'В обробку йде: {obj_ids.count()} ліг.')
    competitions_parse_match_ids(obj_ids)
    print('--- END competitions_parse_match_ids_task')


@shared_task(name='2. Детальний парсинг матчів.')
def parse_matches_data_celery_task():
    print('--- START parse_matches_data_celery_task')
    obj_ids = Match.objects.filter(is_parsed=False).values_list('dota_id', flat=True)
    print(f'В обробку йде: {obj_ids.count()} матчів.')
    parse_matches_data(obj_ids)
    print('--- END parse_matches_data_celery_task')


@shared_task(name='3. Оцінка матчів та формування результату гравців.')
def rate_matches_celery_task():
    print('--- START rate_matches_celery_task')
    obj_ids = Match.objects.filter(is_parsed=True, is_rated=False).values_list('dota_id', flat=True)
    print(f'В обробку йде: {obj_ids.count()} матчів.')
    rate_matches(obj_ids)
    print('--- END rate_matches_celery_task')


@shared_task(name='4. Збереження результатів гравців в систему.')
def save_results_to_player_celery_task():
    print('--- START save_results_to_player_celery_task')
    obj_ids = Match.objects.filter(is_rated=True, is_saved_to_players=False).values_list('dota_id', flat=True)
    print(f'В обробку йде: {obj_ids.count()} матчів.')
    save_results_to_player(obj_ids)
    print('--- END save_results_to_player_celery_task')


@shared_task(name='5. Оновлення фентезі балів.')
def update_fantasy_results_celery_task():
    print('--- START update_fantasy_results')
    obj_ids = CompetitionTour.objects.filter(status='ongoing').values_list('id', flat=True)
    print(f'В обробку йде: {obj_ids.count()} ігрових турів.')
    update_fantasy_results(obj_ids)
    print('--- END update_fantasy_results')


def competitions_parse_match_ids(compt_dota_ids):
    competitions = Competition.objects.filter(dota_id__in=compt_dota_ids)
    for competition in competitions:
        matches_data = api_connector.get_league_matches_id(competition_id=competition.dota_id)
        for match_data in matches_data:
            match_dota_id = match_data.get('match_id')
            series_dota_id = match_data.get('series_id')
            series_type = match_data.get('series_type')
            start_time = match_data.get('start_time')
            radiant_team_id = match_data.get('radiant_team_id')
            dire_team_id = match_data.get('dire_team_id')

            ignore_matches = IgnoreMatch.objects.all().values_list('dota_id', flat=True)

            if str(match_dota_id) in ignore_matches:
                continue

            if match_dota_id and not Match.objects.filter(dota_id=match_dota_id).exists():
                match_datetime = datetime.fromtimestamp(start_time) if start_time else None
                competition_tour = CompetitionTour.objects.filter(
                    competition=competition,
                    start_date__lte=match_datetime,
                    end_date__gte=match_datetime,
                ).first()

                radiant_team = None
                dire_team = None
                if Team.objects.filter(dota_id=radiant_team_id).exists():
                    radiant_team = Team.objects.get(dota_id=radiant_team_id)
                if Team.objects.filter(dota_id=dire_team_id).exists():
                    dire_team = Team.objects.get(dota_id=dire_team_id)

                match_obj = Match.objects.create(
                    dota_id=match_dota_id,
                    competition=competition,
                    competition_tour=competition_tour,
                    team_radiant=radiant_team,
                    team_dire=dire_team,
                    datetime=match_datetime,
                )

                if series_dota_id and series_type is not None:
                    series_obj, _ = MatchSeries.objects.get_or_create(
                        dota_id=series_dota_id,
                        defaults={
                            "bo_format": MatchSeriesBOFormatEnum.get_format(series_type),
                            "competition": competition,
                            "competition_tour": competition_tour,
                        }
                    )
                    match_obj.series = series_obj

                match_obj.is_filled = True
                match_obj.save()


def is_parse_match_data_full(data):
    need_keys = settings.FANTASY_FORMULA.keys()
    player_data = data.get('players', [{}])[0]
    exists_keys = player_data.keys()
    return set(need_keys).issubset(exists_keys)


def parse_matches_data(match_dota_ids, parse_full=True):
    for match_id in match_dota_ids:
        data = api_connector.get_match_info(match_id)
        if data:
            if parse_full and not is_parse_match_data_full(data):
                continue
            Match.objects.filter(dota_id=match_id).update(is_parsed=True, data=data)
        time.sleep(1)


def rate_matches(match_dota_ids):
    matches = Match.objects.filter(dota_id__in=match_dota_ids)
    for match in matches:
        if match.data:
            result = get_result(match)
            match.result_data = result
            match.is_rated = True
            match.save()


def save_results_to_player(match_dota_ids):
    matches = Match.objects.filter(dota_id__in=match_dota_ids)
    for match in matches:
        for account_id, result in match.result_data.items():
            if Player.objects.filter(dota_id=account_id).exists():
                player = Player.objects.get(dota_id=account_id)
                obj, created = PlayerMatchResult.objects.update_or_create(
                    player=player,
                    match=match,
                    defaults={"result": result.get('TOTAL', 0)},
                )
        match.is_saved_to_players = True
        match.save()


def update_fantasy_results(competition_tour_ids):
    qs = CompetitionTour.objects.filter(id__in=competition_tour_ids)
    for tour in qs:
        fan_teams_tour = tour.fantasy_teams.all()
        for fan_team in fan_teams_tour:
            for fan_player in fan_team.fantasy_players.all():
                fan_player.set_result()
            fan_team.set_result()
            fan_team.fantasy_team.set_result()


def result_from_player_data(player_data):
    result = 0
    result_dict = {}

    if not Player.objects.filter(dota_id=player_data.get('account_id')).exists():
        return {}

    player = Player.objects.get(dota_id=player_data.get('account_id'))
    result_dict.update({'NICKNAME': player.nickname, 'TOTAL': result})

    if player.game_role in [GameRoleEnum.CARRY, GameRoleEnum.MID, GameRoleEnum.HARD]:
        pl_role = 'core'
    else:
        pl_role = 'support'

    for action, details in settings.FANTASY_FORMULA.items():
        value = float(player_data.get(action)) if player_data.get(action) is not None else 0
        coef = details.get('coef', {}).get(pl_role, 0)
        action_res = 0

        if details['type'] == '+':
            action_res = round(coef * value, 2)
        elif details['type'] == '-':
            action_res = round(coef * -value, 2)
        if action in ['stuns', 'hero_healing']:
            action_res = action_res if action_res <= 5 else 5
        result += action_res
        result_dict.update({action: action_res})

    win_bonus = 0

    if player_data.get('win', 0):
        win_bonus = abs(result) * 0.1

    result_dict.update({'win_bonus': round(win_bonus, 2)})

    result += win_bonus
    result_dict.update({'TOTAL': round(result, 2)})
    return result_dict


def get_result(match_info):
    match_data = match_info.data
    player_results = {}
    players = match_data.get('players', [])

    for player in players:
        account_id = player.get('account_id')
        if account_id:
            result = result_from_player_data(player)
            player_results[account_id] = result
    return player_results

