from rest_framework import serializers

from fantasy.models import CyberSport, Competition, User, Team, Player, FantasyTeam, FantasyPlayer


class CyberSportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyberSport
        fields = ['id', 'name', 'is_active']


class CompetitionSerializer(serializers.ModelSerializer):
    cyber_sport = CyberSportSerializer()

    class Meta:
        model = Competition
        fields = ['id', 'name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon']


class UserSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id', 'nickname', 'competition']


class TeamSerializer(serializers.ModelSerializer):
    cyber_sport = CyberSportSerializer()

    class Meta:
        model = Team
        fields = ['id', 'name', 'cyber_sport', 'icon']


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'nickname', 'team', 'game_role', 'icon']


class FantasyTeamSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = FantasyTeam
        fields = ['id', 'user', 'competition', 'result', 'name_extended']


class FantasyPlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    player = PlayerSerializer()
    fantasy_team = FantasyTeamSerializer()

    class Meta:
        model = FantasyPlayer
        fields = ['id', 'user', 'player', 'fantasy_team', 'result', 'quantity']

