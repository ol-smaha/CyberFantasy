from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api.serializers import CompetitionSerializer, PlayerSerializer, FantasyTeamSerializer, FantasyPlayerSerializer, \
    UserSerializer
from fantasy.models import Competition, Player, FantasyTeam, FantasyPlayer, User


class CompetitionViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'cyber_sport': ['in', 'exact']
    }


class PlayerViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class FantasyTeamViewSet(mixins.RetrieveModelMixin,
                         GenericViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user': ['in', 'exact']
    }


class FantasyPlayerViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    queryset = FantasyPlayer.objects.all()
    serializer_class = FantasyPlayerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user': ['in', 'exact']
    }


class UserPlayerViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

