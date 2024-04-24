from time import sleep

import requests


class DotaApiConnector:
    BASE_URL = 'https://api.opendota.com/api/'

    @staticmethod
    def get(url, **kwargs):
        headers = kwargs.get('headers') or {}
        response = requests.get(url=url, headers=headers)
        return response

    @staticmethod
    def post(url, json, auth, **kwargs):
        headers = kwargs.get('headers') or {}
        response = requests.get(url=url, json=json, headers=headers, auth=auth)
        return response

    def get_matches_id(self, team_id, competition_id):
        all_matches = []
        url = f'{self.BASE_URL}teams/{team_id}/matches'
        response = self.get(url=url)

        if response.ok:
            data = response.json()

            for match in data:
                match_id = match.get('match_id', 0)
                league_id = str(match.get('leagueid', 0))

                if league_id == competition_id:
                    all_matches.append(match_id)

        else:
            return ''

        return all_matches

    def get_league_matches_id(self, competition_id):
        url = f'{self.BASE_URL}leagues/{competition_id}/matches'
        response = self.get(url=url)
        if response.ok and response.json():
            return response.json()
        else:
            return {}

    def get_match_info(self, id_match):
        url = f'{self.BASE_URL}matches/{id_match}'
        response = self.get(url=url)
        if response.ok:
            return response.json()

        counter = 10
        while counter > 0 and not response.ok:
            counter -= 1
            sleep(1)
            response = self.get(url=url)
            if response.ok:
                return response.json()
        return {}
