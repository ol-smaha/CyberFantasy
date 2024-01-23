from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from django.conf import settings

from fantasy.models import CyberSport, Competition, Team, Player, FantasyTeam, FantasyPlayer
from djoser.serializers import UserCreateSerializer

from users.models import CustomUser

User = get_user_model()


class UserCreateByEmailSerializer(UserCreateSerializer):
    def perform_create(self, validated_data):
        validated_data.update({'username': validated_data.get('email')})
        print(validated_data)
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
        return user

    class Meta(UserCreateSerializer.Meta):
        fields = ['email', 'password', 'username']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']


class CyberSportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyberSport
        fields = ['id', 'name', 'is_active']


class CompetitionSerializer(serializers.ModelSerializer):
    cyber_sport = CyberSportSerializer()

    class Meta:
        model = Competition
        fields = ['id', 'name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon']


class TeamSerializer(serializers.ModelSerializer):
    cyber_sport = CyberSportSerializer()

    class Meta:
        model = Team
        fields = ['id', 'name', 'cyber_sport', 'icon']


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'nickname', 'team', 'game_role', 'icon', 'cost']


class FantasyTeamSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer()

    class Meta:
        model = FantasyTeam
        fields = ['id', 'user', 'competition', 'result', 'name_extended']


class FantasyTeamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FantasyTeam
        fields = ['user', 'competition', 'result', 'name_extended']


class FantasyPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    fantasy_team = FantasyTeamSerializer()

    class Meta:
        model = FantasyPlayer
        fields = ['id', 'user', 'player', 'fantasy_team', 'result']


class FantasyPlayerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FantasyPlayer
        fields = ['user', 'player', 'fantasy_team', 'result']


class FantasyTeamRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = FantasyTeam
        fields = ['user',  'result']

