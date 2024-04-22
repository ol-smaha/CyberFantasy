from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from fantasy.models import Competition, Team, Player, FantasyTeam, FantasyPlayer, PlayerMatchResult, \
    CompetitionTour, FantasyTeamTour
from djoser.serializers import UserCreateSerializer
from rest_framework.authtoken.models import Token


from users.models import CustomUser, AppErrorReport

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


class AppErrorReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppErrorReport
        fields = ['user', 'msg']


class CompetitionTourSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionTour
        fields = ['id', 'name', 'start_date', 'end_date', 'status',
                  'editing_start', 'editing_end', 'is_editing_allowed']


class CompetitionSerializer(serializers.ModelSerializer):
    tours = CompetitionTourSerializer(source='competition_tours', many=True)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'date_start', 'date_finish', 'status', 'icon', 'dota_id', 'active_tour', 'tours']


class CompetitionEditStatusSerializer(serializers.ModelSerializer):
    is_editing_allowed = serializers.SerializerMethodField()
    active_tour = CompetitionTourSerializer()

    class Meta:
        model = Competition
        fields = ['is_editing_allowed', 'active_tour']

    @staticmethod
    def get_is_editing_allowed(obj):
        return obj.is_editing_allowed


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'short_name', 'icon', 'dota_id']


class PlayerSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'nickname', 'team', 'game_role', 'icon', 'cost']


class PlayerMatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerMatchResult
        fields = ['result']


class FantasyPlayerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = FantasyPlayer
        fields = ['id', 'player', 'fantasy_team_tour', 'result']


class FantasyPlayerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FantasyPlayer
        fields = ['player', 'fantasy_team_tour', 'result']


class FantasyTeamSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer()

    class Meta:
        model = FantasyTeam
        fields = ['id', 'user', 'competition', 'result', 'name_extended']


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
        fields = ['id', 'user',  'result']


class FantasyTeamTourSerializer(serializers.ModelSerializer):
    competition_tour = CompetitionTourSerializer()
    fantasy_players = FantasyPlayerSerializer(many=True, required=False)

    class Meta:
        model = FantasyTeamTour
        fields = ['id', 'fantasy_team', 'competition_tour', 'result', 'fantasy_players']


class FantasyTeamTourCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyTeamTour
        fields = ['fantasy_team', 'competition_tour']

    def to_representation(self, instance):
        return FantasyTeamTourSerializer(context=self.context).to_representation(instance)

