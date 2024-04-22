import random
import time
from datetime import datetime


from celery import shared_task
from api.connectors import DotaApiConnector
from fantasy.constants import CompetitionStatusEnum, GameRoleEnum
from fantasy.models import Competition, Match, Player, PlayerMatchResult, CompetitionTour, FantasyPlayer, \
    FantasyTeam, FantasyTeamTour

api_connector = DotaApiConnector()


@shared_task()
def parse_data_matches_from_dota_api():
    print('*'*20)
    print('- START PARSING OPEN DOTA')
    dota_update()
    print('- END PARSING OPEN DOTA')


def parse_matches_for_competition(compt_dota_ids):
    print('parse_matches_for_competition STARTED')
    competitions = Competition.objects.filter(dota_id__in=compt_dota_ids)
    for competition in competitions:
        teams = competition.team.all()
        for team in teams:
            matches_ids = api_connector.get_matches_id(team_id=team.dota_id, competition_id=competition.dota_id)
            for match_id in matches_ids:
                if not Match.objects.filter(dota_id=match_id).exists():
                    Match.objects.create(
                        dota_id=match_id,
                        competition=competition,
                    )
    print('parse_matches_for_competition FINISHED')


def parse_matches_data(match_dota_ids):
    print('parse_matches_data STARTED')
    for match_id in match_dota_ids:
        print(match_id)
        data = api_connector.get_match_info(match_id)
        print(bool(data))
        if data:
            Match.objects.filter(dota_id=match_id).update(is_parsed=True, data=data)
        time.sleep(1)
    print('parse_matches_data FINISHED')


def rate_matches(match_dota_ids):
    print('rate_matches STARTED')
    matches = Match.objects.filter(dota_id__in=match_dota_ids)
    print(matches)
    for match in matches:
        result, match_datetime = get_result(match)
        competition_tour = CompetitionTour.objects.filter(
            competition=match.competition,
            start_date__lte=match_datetime,
            end_date__gte=match_datetime,
        ).first()
        match.result_data = result
        match.datetime = match_datetime
        match.competition_tour = competition_tour
        match.is_rated = True
        match.save()
    print('rate_matches FINISHED')


def save_results_to_player(match_dota_ids):
    print('save_results_to_player STARTED')
    matches = Match.objects.filter(dota_id__in=match_dota_ids)
    for match in matches:
        for account_id, result in match.result_data.items():
            print(result)
            if Player.objects.filter(dota_id=account_id).exists():
                player = Player.objects.get(dota_id=account_id)
                obj, created = PlayerMatchResult.objects.update_or_create(
                    player=player,
                    match=match,
                    defaults={"result": result.get('TOTAL', 0)},
                )
                print(obj, created)
        match.is_saved_to_players = True
        match.save()
    print('save_results_to_player FINISHED')


def update_fantasy_results(competition_tour_ids):
    print('update_fantasy_results STARTED')
    qs = CompetitionTour.objects.filter(id__in=competition_tour_ids)
    for tour in qs:
        fan_teams_tour = tour.fantasy_teams.all()
        for fan_team in fan_teams_tour:
            for fan_player in fan_team.fantasy_players.all():
                fan_player.set_result()
            fan_team.set_result()
            fan_team.fantasy_team.set_result()

    print('update_fantasy_results FINISHED')


def dota_update():
    competitions = Competition.objects.filter(status=CompetitionStatusEnum.STARTED)

    for competition in competitions:
        teams = competition.team.all()
        for team in teams:
            matches_ids = api_connector.get_matches_id(team_id=team.dota_id, competition_id=competition.dota_id)
            for match_id in matches_ids:
                if not Match.objects.filter(dota_id=match_id).exists():
                    match_info = api_connector.get_match_info(match_id)

                    if match_info:
                        Match.objects.create(
                            dota_id=match_id,
                            data=match_info
                        )

                else:
                    print(f"Match {match_id} already exists in MatchInfoDota for Dota competition")


def result_from_player_data(player_data):
    result = 0
    result_dict = {}
    points = {
        'kills': {
            'type': '+',
            'coef': {'core': 2, 'support': 3},
        },
        'deaths': {
            'type': '-',
            'coef': {'core': 2, 'support': 1.5},
        },
        'assists': {
            'type': '+',
            'coef': {'core': 1, 'support': 1},
        },
        'last_hits': {
            'type': '+',
            'coef': {'core': 0.01, 'support': 0.02},
        },
        'denies': {
            'type': '+',
            'coef': {'core': 0.02, 'support': 0.04},
        },
        'hero_damage': {
            'type': '+',
            'coef': {'core': 0.0002, 'support': 0.0002},
        },
        'tower_damage': {
            'type': '+',
            'coef': {'core': 0.0002, 'support': 0.0002},
        },
        'camps_stacked': {
            'type': '+',
            'coef': {'core': 0.15, 'support': 0.25},
        },
        'rune_pickups': {
            'type': '+',
            'coef': {'core': 0.1, 'support': 0.1},
        },
        'obs_placed': {
            'type': '+',
            'coef': {'core': 0.1, 'support': 0.1},
        },
        'sen_placed': {
            'type': '+',
            'coef': {'core': 0.15, 'support': 0.2},
        },
        'observer_kills': {
            'type': '+',
            'coef': {'core': 0.1, 'support': 0.1},
        },
        'sentry_kills': {
            'type': '+',
            'coef': {'core': 0.15, 'support': 0.2},
        },
        'courier_kills': {
            'type': '+',
            'coef': {'core': 1.5, 'support': 1.5},
        },
        'stuns': {
            'type': '+',
            'coef': {'core': 0.1, 'support': 0.1},
        },
        'hero_healing': {
            'type': '+',
            'coef': {'core': 0.001, 'support': 0.0015},
        },
        'buyback_count': {
            'type': '-',
            'coef': {'core': 1.5, 'support': 1.5},
        },
        'teamfight_participation': {
            'type': '+',
            'coef': {'core': 5, 'support': 5},
        },
    }

    player = Player.objects.get(dota_id=player_data.get('account_id'))
    result_dict.update({'NICKNAME': player.nickname, 'TOTAL': result})

    if player.game_role in [GameRoleEnum.CARRY, GameRoleEnum.MID, GameRoleEnum.HARD]:
        pl_role = 'core'
    else:
        pl_role = 'support'

    for action, details in points.items():
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
    match_dtime = None

    for player in players:
        account_id = player.get('account_id')
        match_dtime = datetime.fromtimestamp(player.get('start_time')) if player.get('start_time') else match_dtime
        if account_id:
            result = result_from_player_data(player)
            player_results[account_id] = result
    return player_results, match_dtime

