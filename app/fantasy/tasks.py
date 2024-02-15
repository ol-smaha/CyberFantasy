import random
from datetime import datetime


from celery import shared_task
from api.connectors import DotaApiConnector
from fantasy.constants import CompetitionStatusEnum
from fantasy.models import Competition, MatchInfoDota, Player, PlayerMatchResult, CompetitionTour, FantasyPlayer

api_connector = DotaApiConnector()


@shared_task
def hello():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return a ** b


def dota_update():
    competitions = Competition.objects.filter(cyber_sport__name='Dota', status=CompetitionStatusEnum.STARTED)

    for competition in competitions:
        teams = competition.team.all()
        for team in teams:
            matches_ids = api_connector.get_matches_id(team_id=team.dota_id, competition_id=competition.dota_id)

            for match_id in matches_ids:
                # перевірити чи вже існує такий match_id в MatchInfoDota
                if not MatchInfoDota.objects.filter(dota_id=match_id).exists():
                    match_info = api_connector.get_match_info(match_id)

                    # зберігаємо в базу (MatchInfoDota)
                    MatchInfoDota.objects.create(
                        dota_id=match_id,
                        data=match_info
                    )

                else:
                    print(f"Match {match_id} already exists in MatchInfoDota for Dota competition")


def result_from_player_data(player_data):
    result = 0
    points = {
        'kills': {'type': '+', 'coef': '3.0'},
        'death': {'type': '-', 'coef': '2.0'}
    }

    for action, details in points.items():
        coef = float(details['coef'])

        value = float(player_data.get(action)) if player_data.get(action) is not None else 0

        if details['type'] == '+':
            result += coef * value
        elif details['type'] == '-':
            result -= coef * value

    return result


def get_result(match_info):
    match_data = match_info.data
    player_results = {}
    players = match_data.get('players', [])
    match_date_timestamp = None

    for player in players:
        account_id = player.get('account_id')
        match_date_timestamp = player.get('start_time')
        if account_id:
            result = result_from_player_data(player)
            player_results[account_id] = result
    return player_results, match_date_timestamp


@shared_task()
def evaluate_match_info():
    unrated_matches = MatchInfoDota.objects.filter(is_rated=False)
    # print(unrated_matches)
    results = {}

    for match_info in unrated_matches:
        match_id = match_info.id
        result, match_date_timestamp = get_result(match_info)
        # print(result)
        results[match_id] = {'result': result, 'match_date_timestamp': match_date_timestamp}

        # match_info.is_rated = True
        # match_info.save()
    save_player_match_res(results)
    get_competition_tour(1707230419)

    return results


def save_player_match_res(results):
    print(results)
    for match_id, values in results.items():
        print(match_id)
        print(values)
        results = values.get('result', {})
        match_date_timestamp = values.get('match_date_timestamp')
        competition_tour = get_competition_tour(match_date_timestamp)
        for account_id, result in results.items():
            if Player.objects.filter(dota_id=account_id).exists():
                player = Player.objects.get(dota_id=account_id)

                PlayerMatchResult.objects.create(
                    player=player,
                    match_info_id=match_id,
                    result=result,
                    competition_tour=competition_tour
                )


def get_competition_tour(timestamp):
    match_date = datetime.fromtimestamp(timestamp)
    competition_tour = CompetitionTour.objects.filter(start_date__lte=match_date, end_date__gte=match_date).first()

    fantasy_player = FantasyPlayer.objects.get(id=13)
    print(fantasy_player.player)
    print(fantasy_player.competition_tour)
    player_match_results = PlayerMatchResult.objects.filter(player=fantasy_player.player,
                                                            competition_tour=fantasy_player.competition_tour)
    print(player_match_results)
    return competition_tour

