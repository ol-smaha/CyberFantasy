from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers import CompetitionSerializer, PlayerSerializer, FantasyTeamSerializer, FantasyPlayerSerializer, \
    FantasyTeamCreateSerializer, FantasyPlayerCreateSerializer, FantasyTeamRatingSerializer
from fantasy.models import Competition, Player, FantasyTeam, FantasyPlayer


class CompetitionViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'cyber_sport': ['in', 'exact']
    }

    @action(detail=True, methods=['GET'])
    def rating(self, request, pk=None):
        try:
            competition = self.get_object()
        except Competition.DoesNotExist:
            return Response({"error": "Competition not found"}, status=404)

        fantasy_teams = competition.fantasy_teams.all().order_by('-result')
        serializer = FantasyTeamRatingSerializer(fantasy_teams, many=True)

        return Response(serializer.data)


class PlayerViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'game_role': ['in', 'exact']
    }


class FantasyTeamViewSet(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user': ['in', 'exact']
    }

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FantasyTeamCreateSerializer
        else:
            return self.serializer_class


class FantasyPlayerViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           GenericViewSet):
    queryset = FantasyPlayer.objects.all()
    serializer_class = FantasyPlayerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user': ['in', 'exact']
    }

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FantasyPlayerCreateSerializer
        else:
            return self.serializer_class

