from django.contrib.auth import get_user_model
from django.db import transaction
from requests import Response
from rest_framework import serializers
from fantasy.models import CyberSport, Competition, Team, Player, FantasyTeam, FantasyPlayer
from djoser.serializers import UserCreateSerializer
from rest_framework.authtoken.models import Token


from users.models import CustomUser
User = get_user_model()


class UserCreateByEmailSerializer(UserCreateSerializer):
    token = serializers.CharField(source='auth_token.key', read_only=True)

    def perform_create(self, validated_data):
        username = validated_data.get('username')
        if username:
            validated_data.update({'username': validated_data.get('username')})
        else:
            validated_data.update({'username': validated_data.get('email')})

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            token = Token.objects.create(user=user)
            validated_data.update({'token': token})
        print(validated_data)
        return user

    class Meta(UserCreateSerializer.Meta):
        fields = ['email', 'password', 'username', 'token']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


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
        fields = ['id', 'name', 'date_start', 'date_finish', 'cyber_sport', 'status', 'icon', 'dota_id']


class CompetitionEditStatusSerializer(serializers.ModelSerializer):
    is_editing_allowed = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = ['editing_start', 'editing_end', 'is_editing_allowed']

    @staticmethod
    def get_is_editing_allowed(obj):
        return obj.is_editing_allowed


class TeamSerializer(serializers.ModelSerializer):
    cyber_sport = CyberSportSerializer()

    class Meta:
        model = Team
        fields = ['id', 'name', 'cyber_sport', 'icon', 'dota_id']


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'nickname', 'team', 'game_role', 'icon', 'cost']


class FantasyPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    # fantasy_team = FantasyTeamSerializer()

    class Meta:
        model = FantasyPlayer
        fields = ['id', 'user', 'player', 'fantasy_team', 'result']


class FantasyPlayerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FantasyPlayer
        fields = ['user', 'player', 'fantasy_team', 'result']


class FantasyTeamSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer()
    fantasy_players = FantasyPlayerSerializer(many=True)

    class Meta:
        model = FantasyTeam
        fields = ['id', 'user', 'competition', 'result', 'name_extended', 'fantasy_players']


class FantasyTeamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FantasyTeam
        fields = ['user', 'competition', 'result', 'name_extended']

    def to_representation(self, instance):
        return FantasyTeamSerializer(context=self.context).to_representation(instance)


class FantasyTeamRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = FantasyTeam
        fields = ['user',  'result']

