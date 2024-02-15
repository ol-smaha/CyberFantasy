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

    def get_match_info(self, id_match):
        url = f'{self.BASE_URL}matches/{id_match}'
        response = self.get(url=url)

        if response.ok:
            data = response.json()
            return data


# test = DotaApiConnector()
# res = test.get_matches_id(8376426, 16140)
# print(res)
# res = test.get_match_info(3703866531)
# print(res)
